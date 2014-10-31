/** @file cs4224_diags.c
 ****************************************************************************
 *
 * @brief
 *     This module provides diagnostic methods to assist in debugging
 *     or bringup of the device.
 *
 ****************************************************************************
$copy$
 ***************************************************************************/
#include "diags/cs4224_diags.h"
#include "high_level/cs4224.h"

/* $if : CORTINA : sigtrap */
/* for gdb, use 'raise(SIGTRAP);' when debugging */
#include <signal.h>
/* $endif : CORTINA */

static cs4224_diags_duplex_loopback_state_t g_cs4224_duplex_loopback_line_state[CS4224_MAX_NUM_CS4343_PORTS] = 
{
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}
};
static cs4224_diags_duplex_loopback_state_t g_cs4224_duplex_loopback_host_state[CS4224_MAX_NUM_CS4343_PORTS] =
{
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0},
    {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0,0,0,0,0,0,0,0}
};

static cs4224_diags_simplex_loopback_state_t g_cs4224_simplex_loopback_state[CS4224_MAX_NUM_CS4224_PORTS] = 
{
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}},
    {{FALSE, 0,0,0,0,0,0}, {FALSE, 0,0,0,0,0,0}}
};

cs_uint16 g_cs4224_simplex_valid_mate_slice[CS4224_MAX_NUM_CS4224_PORTS] = 
/* Rx slice     0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15 */
/* Tx slice */ {1, 0, 4, 5, 2, 3, 7, 6,10,11, 8, 9, 15,14,13,12};


/**
 * This method is called to reset any static state used by the
 * driver to manage enabling/disabling of loopbacks.
 *
 * @param slice [I] - The slice/channel of the device to
 *                    reset the state for.
 */
void cs4224_diags_reset_static_state(cs_uint32 slice)
{
    if (cs4224_is_hw_duplex(slice))
    {
        cs4224_diags_duplex_loopback_state_t* state;

        state = &g_cs4224_duplex_loopback_line_state[slice&0x7];
        state->initialized = FALSE;
        
        state = &g_cs4224_duplex_loopback_host_state[slice&0x7];
        state->initialized = FALSE;
    }
    else
    {
        cs4224_diags_simplex_loopback_state_t* state;

        state = &g_cs4224_simplex_loopback_state[slice&0xf];
        state->slice_state.initialized      = FALSE;
        state->mate_slice_state.initialized = FALSE;
    }
}


#if (CS_HAS_DEBUG_LOOPBACKS == 1)

/**
 * This is an internal method used to save the line or host interface
 * context for when a digital loopback is enabled. 
 * This context will be written back to the chip when the
 * digital loopback is tore down.
 * 
 * @param slice  [I] - The slice upon which the loopback is applied.
 * @param intf   [I] - The interface or point where the loopback
 *                     will be set
 * @param state  [O] - A pointer to the structure where the context is saved.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 */
cs_status cs4224_diags_duplex_loopback_save_state(
    cs_uint32                             slice, 
    e_cs4224_loopback_interface           intf,
    cs4224_diags_duplex_loopback_state_t *state) 
{
    cs_status status = CS_OK;

    state->initialized = TRUE;

    if (intf == CS4224_LOOPBK_LINE)
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_STX0_MISC, &(state->stx0_misc));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->line_mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->host_mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RX0_Config, &(state->rx0_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_TX0_Config, &(state->tx0_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXELST0_Control, &(state->rxelst0_control));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, &(state->line_clkout_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, &(state->host_clkout_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, &(state->clkdiv_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_CONTROL, &(state->rxlockd0_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, &(state->line_spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, &(state->host_spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_OPTIONS_SHADOW, &(state->mseq_options));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CPA, &(state->rx_cpa));
    }
    else /* CS4224_LOOPBK_HOST */
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_STX0_MISC, &(state->stx0_misc));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->host_mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->line_mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RX0_Config, &(state->rx0_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_TX0_Config, &(state->tx0_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXELST0_Control, &(state->rxelst0_control));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, &(state->host_clkout_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, &(state->line_clkout_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, &(state->clkdiv_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_CONTROL, &(state->rxlockd0_ctrl));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, &(state->line_spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, &(state->host_spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_OPTIONS_SHADOW, &(state->mseq_options));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CPA, &(state->rx_cpa));
    }

    status |= cs4224_query_edc_mode(slice, CS4224_DPLX_HOST_MSEQ, &(state->host_edc_mode));
    status |= cs4224_query_edc_mode(slice, CS4224_DPLX_LINE_MSEQ, &(state->line_edc_mode));

    return status;
}


/**
 * This is an internal method used to restore the line or host interface
 * context for when a digital loopback is disabled. 
 * 
 * @param slice  [I] - The slice upon which the loopback is applied.
 * @param intf   [I] - The interface or point where the loopback
 *                     will be set
 * @param state  [I] - A pointer to the structure where the context is saved.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 */
cs_status cs4224_diags_duplex_loopback_restore_state(
    cs_uint32                             slice, 
    e_cs4224_loopback_interface           intf,
    cs4224_diags_duplex_loopback_state_t *state) 
{
    cs_status status = CS_OK;

    state->initialized = FALSE;

    if (intf == CS4224_LOOPBK_LINE)
    {
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_STX0_MISC, (state->stx0_misc));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->line_mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->host_mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_RX0_Config, (state->rx0_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_TX0_Config, (state->tx0_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXELST0_Control, (state->rxelst0_control));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, (state->line_clkout_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, (state->host_clkout_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, (state->clkdiv_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_CONTROL, (state->rxlockd0_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, (state->line_spare12));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, (state->host_spare12));
     /* status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_OPTIONS_SHADOW, (state->mseq_options));*/
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CPA, (state->rx_cpa));
    }
    else /* CS4224_LOOPBK_HOST */
    {
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_STX0_MISC, (state->stx0_misc));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->host_mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->line_mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_RX0_Config, (state->rx0_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_TX0_Config, (state->tx0_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXELST0_Control, (state->rxelst0_control));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, (state->host_clkout_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL, (state->line_clkout_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, (state->clkdiv_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_CONTROL, (state->rxlockd0_ctrl));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, (state->line_spare12));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, (state->host_spare12));
     /* status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_OPTIONS_SHADOW, (state->mseq_options));*/
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CPA, (state->rx_cpa));
    }

    return status;
}

/**
 * This is an internal method used to save the interface
 * context for when an simplex loopback is enabled. 
 * This context will be written back to the chip when the
 * simplex loopback is tore down.
 * 
 * @param slice  [I] - The slice upon which the loopback is applied.
 * @param state  [O] - A pointer to the structure where the context is saved.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 */
cs_status cs4224_diags_simplex_loopback_save_state(
    cs_uint32                                   slice, 
    cs4224_diags_simplex_loopback_slice_state_t *state) 
{
    cs_status status = CS_OK;

    state->initialized = TRUE;

    if (cs4224_line_rx_to_host_tx_dir(slice))
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_STX0_MISC, &(state->stx0_misc));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG, &(state->rx_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, &(state->spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_DFE_CONFIG, &(state->dfe_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_AGC_CONFIG1, &(state->agc_config1));
    }
    else
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_STX0_MISC, &(state->stx0_misc));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CONFIG, &(state->rx_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, &(state->mseq_power_down));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, &(state->spare12));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_DFE_CONFIG, &(state->dfe_config));
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_AGC_CONFIG1, &(state->agc_config1));
    }

    return status;
}

/**
 * This is an internal method used to restore the line or host interface
 * context for when an simplex loopback is tore down. 
 * 
 * @param slice  [I] - The slice upon which the loopback is applied.
 * @param state  [O] - A pointer to the structure where the context is saved.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 */
cs_status cs4224_diags_simplex_loopback_restore_state(
    cs_uint32                                   slice, 
    cs4224_diags_simplex_loopback_slice_state_t *state) 
{
    cs_status status = CS_OK;

    state->initialized = FALSE;

    if (cs4224_line_rx_to_host_tx_dir(slice))
    {
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_STX0_MISC, (state->stx0_misc));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG, (state->rx_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, (state->spare12));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_DFE_CONFIG, (state->dfe_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_AGC_CONFIG1, (state->agc_config1));
    }
    else
    {
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_STX0_MISC, (state->stx0_misc));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CONFIG, (state->rx_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, (state->mseq_power_down));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, (state->spare12));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_DFE_CONFIG, (state->dfe_config));
        status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_COMMON_SRX0_AGC_CONFIG1, (state->agc_config1));
    }

    return status;
}


/* $if : CORTINA : Only for internal use */
/**
 * This is an internal method used to dump the simplex loopback saved interface context
 * 
 * @private
 */
void cs4224_diags_simplex_loopback_dump_state(
cs4224_diags_simplex_loopback_state_t* state)
{
    CS_PRINTF(("\nSimplex Loopback Saved State Table"));

    CS_PRINTF(("\nSlice,      Initialized                 : %s",       state->slice_state.initialized? "TRUE    ": "FALSE   "));
    CS_PRINTF(("\nSlice,      SDS_COMMON_STX0_MISC        : 0x%04x, ", state->slice_state.stx0_misc));
    CS_PRINTF(("\nSlice,      SDS_COMMON_SRX0_RX_CONFIG   : 0x%04x, ", state->slice_state.rx_config));
    CS_PRINTF(("\nSlice,      SDS_DSP_MSEQ_POWER_DOWN_LSB : 0x%04x, ", state->slice_state.mseq_power_down));
    CS_PRINTF(("\nSlice,      SDS_DSP_MSEQ_SPARE12_LSB    : 0x%04x, ", state->slice_state.spare12));
    CS_PRINTF(("\nSlice,      SDS_COMMON_SRX0_DFE_CONFIG  : 0x%04x, ", state->slice_state.dfe_config));
    CS_PRINTF(("\nSlice,      SDS_COMMON_SRX0_AGC_CONFIG1 : 0x%04x, ", state->slice_state.agc_config1));
    CS_PRINTF(("\nMate Slice, Initialized                 : %s",       state->mate_slice_state.initialized? "TRUE    ": "FALSE   "));
    CS_PRINTF(("\nMate Slice, SDS_COMMON_STX0_MISC        : 0x%04x, ", state->mate_slice_state.stx0_misc));
    CS_PRINTF(("\nMate Slice, SDS_COMMON_SRX0_RX_CONFIG   : 0x%04x, ", state->mate_slice_state.rx_config));
    CS_PRINTF(("\nMate Slice, SDS_DSP_MSEQ_POWER_DOWN_LSB : 0x%04x, ", state->mate_slice_state.mseq_power_down));
    CS_PRINTF(("\nMate Slice, SDS_DSP_MSEQ_SPARE12_LSB    : 0x%04x, ", state->mate_slice_state.spare12));
    CS_PRINTF(("\nMate Slice, SDS_COMMON_SRX0_DFE_CONFIG  : 0x%04x, ", state->mate_slice_state.dfe_config));
    CS_PRINTF(("\nMate Slice, SDS_COMMON_SRX0_AGC_CONFIG1 : 0x%04x, ", state->mate_slice_state.agc_config1));
    CS_PRINTF(("\n"));
    
}
/* $endif : CORTINA */


/* $if : CORTINA : Only for internal use */
/**
 * This is an internal method used to dump the digital loopback saved interface context
 * 
 * @private
 */
void cs4224_diags_duplex_loopback_dump_state(
        cs4224_diags_duplex_loopback_state_t* state)
{
    CS_PRINTF(("\nDigital Loopback Saved State Table"));

    CS_PRINTF(("\nInitialized                         : %s",     state->initialized? "TRUE    ": "FALSE   "));
    CS_PRINTF(("\nSDS_COMMON_STX0_MISC                : 0x%04x", state->stx0_misc));
    CS_PRINTF(("\nLINE_SDS_DSP_MSEQ_POWER_DOWN_LSB    : 0x%04x", state->line_mseq_power_down));
    CS_PRINTF(("\nHOST_SDS_DSP_MSEQ_POWER_DOWN_LSB    : 0x%04x", state->host_mseq_power_down));
    CS_PRINTF(("\nSDS_COMMON_RX0_Config               : 0x%04x", state->rx0_config));
    CS_PRINTF(("\nSDS_COMMON_TX0_Config               : 0x%04x", state->tx0_config));
    CS_PRINTF(("\nSDS_COMMON_RXELST0_Control          : 0x%04x", state->rxelst0_control));
    CS_PRINTF(("\nLINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL : 0x%04x", state->line_clkout_ctrl));
    CS_PRINTF(("\nHOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL : 0x%04x", state->host_clkout_ctrl));
    CS_PRINTF(("\nSDS_COMMON_SRX0_RX_CLKDIV_CTRL      : 0x%04x", state->clkdiv_ctrl));
    CS_PRINTF(("\nSDS_COMMON_RXLOCKD0_CONTROL         : 0x%04x", state->rxlockd0_ctrl));
    CS_PRINTF(("\nLINE_SDS_DSP_MSEQ_SPARE12_LSB       : 0x%04x", state->line_spare12));
    CS_PRINTF(("\nHOST_SDS_DSP_MSEQ_SPARE12_LSB       : 0x%04x", state->host_spare12));
    CS_PRINTF(("\nLINE_SDS_COMMON_SRX0_RX_CPA         : 0x%04x", state->rx_cpa));
    CS_PRINTF(("\n"));
}
/* $endif : CORTINA */

/**
 * This method queries the Duplex loopbacks on a port-pair slice of a Duplex device.
 * It is called to read the loopback type applied (if any) on the line and host interfaces
 * of the device. This method supports line/host near/far digital loopbacks. 
 * 
 *                     Line             Host
 *                    +---------------------+
 *                Rx -+---------->----------+- Tx ingress
 *                    | )   ( Digital )   ( |
 *                Tx -+----------<----------+- Rx egress
 *                    +---------------------+
 *                      1   2         3   4
 *              
 *                  Legend:
 *                  - 1, Line Digital Near
 *                  - 2, Host Digital Far
 *                  - 3, Line Digital Far
 *                  - 4, Host Digital Near
 *    
 * @param slice         [I] - The slice to the port of the device to access 
 * @param line_lb_type  [O] - The line interface loopback. 
 * @param host_lb_type  [O] - The host interface loopback. 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_query_loopbacks(
    cs_uint32           slice,
    e_cs4224_loopback*  line_lb_type,
    e_cs4224_loopback*  host_lb_type)
{
    cs_status status = CS_OK;
    cs_uint16 data;

    *line_lb_type = CS4224_LOOPBK_DUPLEX_NONE;
    *host_lb_type = CS4224_LOOPBK_DUPLEX_NONE;

    if (cs4224_is_hw_simplex(slice))
    {
        CS_PRINTF(("ERROR: Loopbacks query supported on Duplex chips only\n"));
        return CS_ERROR;
    }

    status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RX0_Config, &data);
    if ((data & 0x0001) == 0x0001)
    {
        /* data_source = TX Loopback Data */
        *line_lb_type = CS4224_LOOPBK_DUPLEX_FAR_DATA;
    }
    else
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_TX0_Config, &data);
        if ((data & 0x0003) == 0x0002)
        {
            /* data_source = RX Loopback Data */
            *line_lb_type = CS4224_LOOPBK_DUPLEX_NEAR_DATA;
        }
    }

    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RX0_Config, &data);
    if ((data & 0x0001) == 0x0001)
    {
        /* data_source = TX Loopback Data */
        *host_lb_type = CS4224_LOOPBK_DUPLEX_FAR_DATA;
    }
    else
    {
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_TX0_Config, &data);
        if ((data & 0x0003) == 0x0002)
        {
            /* data_source = RX Loopback Data */
            *host_lb_type = CS4224_LOOPBK_DUPLEX_NEAR_DATA;
        }
    }
  
    return status;

}

/* $if : CORTINA : Only for regression */
/**
 * This wrapper method queries loopbacks applied (if any) on a port-pair 
 * slice of a duplex devices. The line and host loopacks type(s), if any, are returned
 * in the supplied type argument. This wrapper method used for python scripting
 * only.
 *    
 * @param slice         [I] - The slice to the port of the device to access 
 * @param type          [O] - The line and host loopback types applied
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_query_loopbacks_wrapper(
    cs_uint32           slice,
    cs_uint32           *type)
{
    cs_status status = CS_OK;
    e_cs4224_loopback line_lb_type, host_lb_type;

    status |= cs4224_diags_query_loopbacks(slice, &line_lb_type, &host_lb_type);

    *type = 0;
    *type |= (cs_uint32)line_lb_type << 8; 
    *type |= (cs_uint32)host_lb_type; 

    return status;
}
/* $endif : CORTINA */

/**
 * This method queries then dumps the Duplex loopbacks applied (if any) on a port-pair 
 * slice of a duplex devices.
 *    
 * @param slice         [I] - The slice to the port of the device to access 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_dump_loopbacks(
    cs_uint32  slice)
{
    cs_status status = CS_OK;
    e_cs4224_loopback line_lb_type, host_lb_type;

    status |= cs4224_diags_query_loopbacks(slice, &line_lb_type, &host_lb_type);
         
    CS_PRINTF(("+-----------------------------------+\n"));
    CS_PRINTF(("| Loopbacks Applied to Slice %2x     |\n",slice));
    CS_PRINTF(("+-----------------------------------+\n"));
    CS_PRINTF(("|   Line: "));
  
    if (line_lb_type == CS4224_LOOPBK_DUPLEX_NEAR_DATA)
    {
        CS_PRINTF((" Duplex Near              |\n"));
    } 
    else if (line_lb_type == CS4224_LOOPBK_DUPLEX_FAR_DATA)
    {
        CS_PRINTF((" Duplex Far               |\n"));
    }
    else
    {
        CS_PRINTF((" None                     |\n"));
    }
        
    CS_PRINTF(("|   Host: "));
    if (host_lb_type == CS4224_LOOPBK_DUPLEX_NEAR_DATA)
    {
        CS_PRINTF((" Duplex Near              |\n"));
    } 
    else if (host_lb_type == CS4224_LOOPBK_DUPLEX_FAR_DATA)
    {
        CS_PRINTF((" Duplex Far               |\n"));
    }
    else
    {
        CS_PRINTF((" None                     |\n"));
    }
    CS_PRINTF(("+-----------------------------------+\n"));

    return status;
}

/**
 * This method supports Digital loopbacks on a port-pair slice of a Duplex devices.
 * It is called to enable/disable loopbacks on one of the interfaces 
 * that the device supports. This method supports line/host near/far digital 
 * loopbacks. 
 * 
 * Digital Near loopbacks cannot co-exist with Digital Far loopbacks 
 * ie if an attempt is made to apply a Line Digital Near loopback while 
 * a Line Digital Far loopback is applied, the request will be refused 
 * with an error mesage. Line and Host loopbacks are independant of 
 * each other.
 * 
 * Illustration of the Digital loopback on a duplex port-pair slice.
 *    
 *                     Line             Host
 *                    +---------------------+
 *                Rx -+---------->----------+- Tx ingress
 *                    | )   ( Digital )   ( |
 *                Tx -+----------<----------+- Rx egress
 *                    +---------------------+
 *                      1   2         3   4
 *              
 *                  Legend:
 *                  - 1, Line Digital Near
 *                  - 2, Host Digital Far
 *                  - 3, Line Digital Far
 *                  - 4, Host Digital Near
 *    
 * Note: Loopbacks should only be used on a duplex device. Loopbacks
 *       cannot be combined with 2x2 protection switching.
 *
 * @param slice    [I] - The slice to the port of the device to access 
 * @param lb_type  [I] - The interface to loopback. 
 * @param intf     [I] - The interface or point where the loopback
 *                       will be set
 * @param enable   [I] - TRUE to enable the loopback or FALSE to disable the loopback
 * @param state    [I] - A pointer to a structure containg state information
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 *
 */
cs_status cs4224_diags_duplex_loopback_set(
    cs_uint32                             slice,
    e_cs4224_loopback                     lb_type,
    e_cs4224_loopback_interface           intf,
    cs_uint8                              enable,
    cs4224_diags_duplex_loopback_state_t* state)
{
    cs_status status = CS_OK;
    cs_uint16 data = 0;
    cs4224_rules_t rules;
    cs_boolean k2a2 = FALSE;

    if (cs4224_is_hw_simplex(slice))
    {
        CS_PRINTF(("ERROR: Digital loopbacks supported on Duplex chips only\n"));
        return CS_ERROR;
    }
    /* Note that we can only have one type of loopback enabled at any time, 
       either a near or far digital loopback. The following
       section will bail out of this method with an error code if a near or
       far loopback is already applied. Line and host digital loopbacks can
       be applied at the same time however. Also note that the above static
       variables do not persist accross multiple python method calls. Use method
       cs4224_debug_loopback test for initialized flag testing.
    */
    
    /* Because we are not provided the configuration rules, we define some of them here 
        so that when we call edc_mode_intf to switch to SR, it will configure the bare minimum.
    */
    rules.application = CS4224_TARGET_APPLICATION_10G; /* define app as 10G so as to avoid CPA modifications */
    rules.rx_if.dplx_line_eq.traceloss = CS_HSIO_TRACE_LOSS_LAB; /* avoid equalizer changes */
    rules.rx_if.dplx_host_eq.traceloss = CS_HSIO_TRACE_LOSS_LAB; /* avoid equalizer changes */
    rules.advanced.phsel_bypass = FALSE; /* This should (almost) always be False */

    cs4224_lock(slice);

    if (enable)
    {
        if (intf == CS4224_LOOPBK_LINE)
        {
            /* check to see if Digital Near loopback already applied */
            if (state->initialized)
            {
                CS_PRINTF(("ERROR: Digital loopback already applied\n"));
                cs4224_unlock(slice);
                return CS_ERROR;
            }
            /* save context prior to applying loopback to be restored when loopbacks are tore down */
            status = cs4224_diags_duplex_loopback_save_state(slice, CS4224_LOOPBK_LINE, state);

            /* if microsequencer is running */
            if (0 == (0x0008 & state->mseq_options)) 
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, TRUE);
            }

            if ((state->host_edc_mode != CS_HSIO_EDC_MODE_DISABLED) &&
                (state->host_edc_mode != CS_HSIO_EDC_MODE_SR))  
            {
                /* force host side EDC mode to SR
                 * Note: we don't care about traceloss here because the pre-eq
                 *   won't be used in a loopback, even if traceloss is garbage
                 */
                rules.rx_if.dplx_host_edc_mode = CS_HSIO_EDC_MODE_SR;
                status |= cs4224_init_edc_mode_intf(slice, &rules, CS4224_DPLX_HOST_MSEQ);
            }
        }
        else /* CS4224_LOOPBK_HOST */
        {
            /* check to see if Digital Near loopback already applied */
            if (state->initialized)
            {
                CS_PRINTF(("ERROR: Digital loopback already applied\n"));
                cs4224_unlock(slice);
                return CS_ERROR;
            }
            /* save context prior to applying loopback to be restored when loopbacks are tore down */
            status = cs4224_diags_duplex_loopback_save_state(slice, CS4224_LOOPBK_HOST, state);

            /* if microsequencer is running */
            if (0 == (0x0008 & state->mseq_options)) 
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, TRUE);
            }

            if ((state->line_edc_mode != CS_HSIO_EDC_MODE_DISABLED) &&
                (state->line_edc_mode != CS_HSIO_EDC_MODE_SR))  
            {
                /* force line side EDC mode to SR
                 * Note: we don't care about traceloss here because the pre-eq
                 *   won't be used in a loopback, even if traceloss is garbage
                 */
                rules.rx_if.dplx_line_edc_mode = CS_HSIO_EDC_MODE_SR;
                status |= cs4224_init_edc_mode_intf(slice, &rules, CS4224_DPLX_LINE_MSEQ);
            }
        }
    }
    else /* disable */
    {
        cs_boolean stalled = TRUE;
        
        if (intf == CS4224_LOOPBK_LINE)
        {
            if (!state->initialized)
            {
                CS_TRACE(("ERROR: Digital loopback not applied\n"));
                cs4224_unlock(slice);
                return CS_ERROR;
            }
            
            /* warning about known limitation of this release */
            CS_TRACE(("WARNING: This method does not fully revert loopback state on the line side of slice 0x%x, this is a known limitation.\n", slice));
            
            /* stall LINE mseq while making changes */
            status |= cs4224_query_mseq_is_stalled(slice, CS4224_DPLX_LINE_MSEQ, &stalled);
            if(!stalled)
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, TRUE);
            }
            
            /* restore context to restore data-path to the state is was in prior to applying the loopback */
            status = cs4224_diags_duplex_loopback_restore_state(slice, CS4224_LOOPBK_LINE, state);

            if ((state->host_edc_mode != CS_HSIO_EDC_MODE_DISABLED) &&
                (state->host_edc_mode != CS_HSIO_EDC_MODE_SR))  
            {
                /* restore the host side EDC mode */
                rules.rx_if.dplx_host_edc_mode = state->host_edc_mode;
                /* traceloss only used in SR, don't care about restoring it */
                status |= cs4224_init_edc_mode_intf(slice, &rules, CS4224_DPLX_HOST_MSEQ);

                /* Revert the power savings register */
                status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB, state->host_spare12);
            }

            /* if HOST mseq was previously running */
            if (0 == (0x0008 & state->mseq_options)) 
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, FALSE);
            }
            
            /* unstall LINE mseq if it was running before we started this block */
            if(!stalled)
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, FALSE);
            }
        }
        else /* CS4224_LOOPBK_HOST */
        {
            if (!state->initialized)
            {
                CS_TRACE(("ERROR: Digital loopback not applied\n"));
                cs4224_unlock(slice);
                return CS_ERROR;
            }
            
            /* warning about known limitation of this release */
            CS_TRACE(("WARNING: This method does not fully revert loopback state on the host side of slice 0x%x, this is a known limitation.\n", slice));
            
            /* stall HOST mseq while making changes */
            status |= cs4224_query_mseq_is_stalled(slice, CS4224_DPLX_HOST_MSEQ, &stalled);
            if(!stalled)
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, TRUE);
            }
            
            /* restore context to restore data-path to the state is was in prior to applying the loopback */
            status = cs4224_diags_duplex_loopback_restore_state(slice, CS4224_LOOPBK_HOST, state);

            if ((state->line_edc_mode != CS_HSIO_EDC_MODE_DISABLED) &&
                (state->line_edc_mode != CS_HSIO_EDC_MODE_SR))  
            {
                /* restore the line side EDC mode */
                rules.rx_if.dplx_line_edc_mode = state->line_edc_mode;
                /* traceloss only used in SR, don't care about restoring it */
                status |= cs4224_init_edc_mode_intf(slice, &rules, CS4224_DPLX_LINE_MSEQ);

                /* Revert the power savings register */
                status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, state->line_spare12);
            }
            
            /* if LINE mseq was previously running */
            if (0 == (0x0008 & state->mseq_options)) 
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, FALSE);
            }
            
            /* unstall HOST mseq if it was running before we started this block */
            if(!stalled)
            {
                status |= cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, FALSE);
            }
        }

        /* re-synch the elastic stores */
        cs4224_resync_elsto(slice, CS4224_PP_LINE_SDS_COMMON_RXELST0_Control);
        cs4224_resync_elsto(slice, CS4224_PP_LINE_SDS_COMMON_TXELST0_Control);
        cs4224_resync_elsto(slice, CS4224_PP_HOST_SDS_COMMON_RXELST0_Control);
        cs4224_resync_elsto(slice, CS4224_PP_HOST_SDS_COMMON_TXELST0_Control);

        cs4224_unlock(slice);

        return status;
    }

    /* K2A2 has reworked loopbacks that need special settings
     * top bits of CHIP_ID_MSB are the version, with k2a2 being 0x7
     * this should work with all variants
     */
    status |= cs4224_reg_get_channel(slice, CS4224_GLOBAL_CHIP_ID_MSB, &data);
    if((data & 0xF000) == 0x7000)
    {
        k2a2 = TRUE;
    }
    else
    {
        k2a2 = FALSE;
    }

    switch(lb_type)
    {
        /* Line and Host Interface Data Loopbacks in data sheet
         *
         * In order to setup the loopbacks it is necessary to set
         * looback enable bits in both the receiver and the transmitter.
         * Setting only one of the bits will cause problems.
         */

        cs_uint16 stx0_misc_addr;
        cs_uint16 rx0_config_addr;
        cs_uint16 tx0_config_addr;
        cs_uint16 clkout_ctrl_div64out_addr;
        cs_uint16 clkout_ctrl_refclk_addr;
        cs_uint16 rxcdr_clkdiv_ctrl_addr;
        cs_uint16 pfdcdr_clkdiv_ctrl_addr;
        cs_uint16 rxlockd0_ctrl_addr;
        cs_uint16 rxelst0_ctrl_addr;
        cs_uint16 txelst0_ctrl_addr;
        cs_uint16 txelst0_ctrl_addr_2;
        cs_uint16 line_mseq_spare12;
        cs_uint16 host_mseq_spare12;
        cs_uint16 squelch;
        cs_uint16 rx_cpa_addr;
        cs_uint16 rx_config_addr;

        case CS4224_LOOPBK_DUPLEX_NEAR_DATA:
        {
            if (intf == CS4224_LOOPBK_LINE)
            {
                /* CS_PRINTF(("Applying a Digital Line Near Loopback\n")); */
                stx0_misc_addr            = CS4224_PP_LINE_SDS_COMMON_STX0_MISC;
                tx0_config_addr           = CS4224_PP_LINE_SDS_COMMON_TX0_Config;
                clkout_ctrl_div64out_addr = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                clkout_ctrl_refclk_addr   = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                pfdcdr_clkdiv_ctrl_addr   = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxcdr_clkdiv_ctrl_addr    = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxlockd0_ctrl_addr        = CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_CONTROL;
                rxelst0_ctrl_addr         = CS4224_PP_LINE_SDS_COMMON_RXELST0_Control;
                txelst0_ctrl_addr         = CS4224_PP_LINE_SDS_COMMON_TXELST0_Control;
                line_mseq_spare12         = CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB;
                host_mseq_spare12         = CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB;
                squelch                   = CS4224_PP_LINE_SDS_COMMON_STX0_SQUELCH;
                rx_cpa_addr               = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CPA;
                rx_config_addr            = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG;
            }
            else
            {
                /* CS_PRINTF(("Applying a Digital Host Near Loopback\n")); */
                stx0_misc_addr            = CS4224_PP_HOST_SDS_COMMON_STX0_MISC;
                tx0_config_addr           = CS4224_PP_HOST_SDS_COMMON_TX0_Config;
                clkout_ctrl_div64out_addr = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                clkout_ctrl_refclk_addr   = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                pfdcdr_clkdiv_ctrl_addr   = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxcdr_clkdiv_ctrl_addr    = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxlockd0_ctrl_addr        = CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_CONTROL;
                rxelst0_ctrl_addr         = CS4224_PP_HOST_SDS_COMMON_RXELST0_Control;
                txelst0_ctrl_addr         = CS4224_PP_HOST_SDS_COMMON_TXELST0_Control;
                line_mseq_spare12         = CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB;
                host_mseq_spare12         = CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB;
                squelch                   = CS4224_PP_HOST_SDS_COMMON_STX0_SQUELCH;
                rx_cpa_addr               = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CPA;
                rx_config_addr            = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CONFIG;
            }

            status |= cs4224_reg_get_channel(slice, line_mseq_spare12, &data);
            data &= ~0x0006; /* disable squelch and power savings */
            status |= cs4224_reg_set_channel(slice, line_mseq_spare12, data);

            status |= cs4224_reg_get_channel(slice, host_mseq_spare12, &data);
            data &= ~0x0006; /* disable squelch and power savings */
            status |= cs4224_reg_set_channel(slice, host_mseq_spare12, data);

            status |= cs4224_reg_get_channel(slice, stx0_misc_addr, &data);
            data &= ~0x11; /* power-up mux, STX_EYEMODE_EN=0 */
            status |= cs4224_reg_set_channel(slice, stx0_misc_addr, data);

            /* disable squelch on the Tx of the opposite interface */
            status = cs4224_reg_set_channel(slice, squelch, 0x0000);

            /* elastic stores require the other demux clock powered up, so trickle power-up both */ 
            status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x001f);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x001f);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x0000);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x0000);

            status |= cs4224_reg_get_channel(slice, tx0_config_addr, &data);
            data |= 0x001a;  /* data_source is RX loopback data, BITSWAP True */
            status |= cs4224_reg_set_channel(slice, tx0_config_addr, data);
            
            if(k2a2)
            {
                /*rxcdr fastdiv_sel to div by 16 */
                status |= cs4224_reg_get_channel(slice, rxcdr_clkdiv_ctrl_addr, &data);
                data = CS_CLR(data, 0xf000);
                data = CS_SET(data, 0x1000);
                status |= cs4224_reg_set_channel(slice, rxcdr_clkdiv_ctrl_addr, data);
                
                /*pfdcdr rdiv to div by 16, ct[rv]div to div by 8 */
                status |= cs4224_reg_get_channel(slice, pfdcdr_clkdiv_ctrl_addr, &data);
                data = CS_CLR(data, 0x0f0f);
                data = CS_SET(data, 0x0f01);
                status |= cs4224_reg_set_channel(slice, pfdcdr_clkdiv_ctrl_addr, data);
                
                status |= cs4224_reg_get_channel(slice, rx_config_addr, &data);
                if (data & CS_BIT7)
                {
                    /* the ring oscillator requires different settings */
                    status |= cs4224_reg_set_channel(slice, rx_cpa_addr, 0x0044);
                }
                else
                {
                    /*rxcdr's rx_cpa to 0x99 */
                    status |= cs4224_reg_set_channel(slice, rx_cpa_addr, 0x0099);
                }
            }
            else
            {
                /*rxcdr div by 64 */
                status |= cs4224_reg_get_channel(slice, clkout_ctrl_div64out_addr, &data);
                data |= 0x4000;  /* SRX_DIV64OUT_EN True */
                status |= cs4224_reg_set_channel(slice, clkout_ctrl_div64out_addr, data);

                /*pfdcdr div by 64 */
                status |= cs4224_reg_get_channel(slice, pfdcdr_clkdiv_ctrl_addr, &data);
                data &= ~0x000f;
                data |= 0x0004;  /* SRX_RDIV_SEL = div by 64 */
                status |= cs4224_reg_set_channel(slice, pfdcdr_clkdiv_ctrl_addr, data);
            }
            
            /* PFD mode on the pfdcdr */
            status |= cs4224_reg_get_channel(slice, clkout_ctrl_refclk_addr, &data);
            data |= 0x8000;  /* SRX_REFCLK_SEL True */
            status |= cs4224_reg_set_channel(slice, clkout_ctrl_refclk_addr, data);

            status |= cs4224_reg_get_channel(slice, rxlockd0_ctrl_addr, &data);
            data |= 0x0001;  /* PD_MODE=0 and FORCE_LOCK=1 */
            status |= cs4224_reg_set_channel(slice, rxlockd0_ctrl_addr, data);

            /* re-synch the elastic stores */
            cs4224_resync_elsto(slice, rxelst0_ctrl_addr);
            cs4224_resync_elsto(slice, txelst0_ctrl_addr);
            
            break;
        }

        case CS4224_LOOPBK_DUPLEX_FAR_DATA:
        {
            if (intf == CS4224_LOOPBK_LINE)
            {
                /* CS_PRINTF(("Applying a Digital Line Far Loopback\n")); */
                stx0_misc_addr            = CS4224_PP_LINE_SDS_COMMON_STX0_MISC;
                rx0_config_addr           = CS4224_PP_HOST_SDS_COMMON_RX0_Config;
                tx0_config_addr           = CS4224_PP_LINE_SDS_COMMON_TX0_Config;
                clkout_ctrl_div64out_addr = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                clkout_ctrl_refclk_addr   = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                pfdcdr_clkdiv_ctrl_addr   = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxcdr_clkdiv_ctrl_addr    = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxlockd0_ctrl_addr        = CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_CONTROL;
                rxelst0_ctrl_addr         = CS4224_PP_HOST_SDS_COMMON_RXELST0_Control;
                txelst0_ctrl_addr         = CS4224_PP_HOST_SDS_COMMON_TXELST0_Control;
                txelst0_ctrl_addr_2       = CS4224_PP_LINE_SDS_COMMON_TXELST0_Control;
                line_mseq_spare12         = CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB;
                host_mseq_spare12         = CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB;
                squelch                   = CS4224_PP_LINE_SDS_COMMON_STX0_SQUELCH;
                rx_cpa_addr               = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CPA;
                rx_config_addr            = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG;
            }
            else
            {
                /* CS_PRINTF(("Applying a Digital Host Far Loopback\n")); */
                stx0_misc_addr            = CS4224_PP_HOST_SDS_COMMON_STX0_MISC;
                rx0_config_addr           = CS4224_PP_LINE_SDS_COMMON_RX0_Config;
                tx0_config_addr           = CS4224_PP_HOST_SDS_COMMON_TX0_Config;
                clkout_ctrl_div64out_addr = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                clkout_ctrl_refclk_addr   = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKOUT_CTRL;
                pfdcdr_clkdiv_ctrl_addr   = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxcdr_clkdiv_ctrl_addr    = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
                rxlockd0_ctrl_addr        = CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_CONTROL;
                rxelst0_ctrl_addr         = CS4224_PP_LINE_SDS_COMMON_RXELST0_Control;
                txelst0_ctrl_addr         = CS4224_PP_LINE_SDS_COMMON_TXELST0_Control;
                txelst0_ctrl_addr_2       = CS4224_PP_HOST_SDS_COMMON_TXELST0_Control;
                line_mseq_spare12         = CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB;
                host_mseq_spare12         = CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB;
                squelch                   = CS4224_PP_HOST_SDS_COMMON_STX0_SQUELCH;
                rx_cpa_addr               = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CPA;
                rx_config_addr            = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CONFIG;
            }

            status |= cs4224_reg_get_channel(slice, line_mseq_spare12, &data);
            data &= ~0x0006; /* disable squelch and power savings */
            status |= cs4224_reg_set_channel(slice, line_mseq_spare12, data);

            status |= cs4224_reg_get_channel(slice, host_mseq_spare12, &data);
            data &= ~0x0006; /* disable squelch and power savings */
            status |= cs4224_reg_set_channel(slice, host_mseq_spare12, data);

            status |= cs4224_reg_get_channel(slice, stx0_misc_addr, &data);
            data &= ~0x11; /* power-up mux, STX_EYEMODE_EN=0 */
            status |= cs4224_reg_set_channel(slice, stx0_misc_addr, data);

            /* disable squelch on the Tx of the opposite interface */
            status = cs4224_reg_set_channel(slice, squelch, 0x0000);

            /* elastic stores require the other demux clock powered up, so tricle power-up both */ 
            status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x001f);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x001f);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x0000);
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB, 0x0000);

            status |= cs4224_reg_get_channel(slice, rx0_config_addr, &data);
            data |= 0x0001;  /* data_source is TX loopback data */
            status |= cs4224_reg_set_channel(slice, rx0_config_addr, data);

            status |= cs4224_reg_get_channel(slice, tx0_config_addr, &data);
            data |= 0x0018;  /* data_source is DIG_TX_DIN, BITSWAP True */
            status |= cs4224_reg_set_channel(slice, tx0_config_addr, data);

            status |= cs4224_reg_get_channel(slice, rxelst0_ctrl_addr, &data);
            data &= ~0x0002;  /* do not use USE_LOCKDET True */
            status |= cs4224_reg_set_channel(slice, rxelst0_ctrl_addr, data);

            if(k2a2)
            {
                /*rxcdr fastdiv_sel to div by 16 */
                status |= cs4224_reg_get_channel(slice, rxcdr_clkdiv_ctrl_addr, &data);
                data = CS_CLR(data, 0xf000);
                data = CS_SET(data, 0x1000);
                status |= cs4224_reg_set_channel(slice, rxcdr_clkdiv_ctrl_addr, data);
                
                /*pfdcdr rdiv to div by 16, ct[rv]div to div by 8 */
                status |= cs4224_reg_get_channel(slice, pfdcdr_clkdiv_ctrl_addr, &data);
                data = CS_CLR(data, 0x0f0f);
                data = CS_SET(data, 0x0f01);
                status |= cs4224_reg_set_channel(slice, pfdcdr_clkdiv_ctrl_addr, data);
                
                status |= cs4224_reg_get_channel(slice, rx_config_addr, &data);
                if (data & CS_BIT7)
                {
                    /* the ring oscillator requires different settings */
                    status |= cs4224_reg_set_channel(slice, rx_cpa_addr, 0x0044);
                }
                else
                {
                    /*rxcdr's rx_cpa to 0x99 */
                    status |= cs4224_reg_set_channel(slice, rx_cpa_addr, 0x0099);
                }
            }
            else
            {
                /*rxcdr div by 64 */
                status |= cs4224_reg_get_channel(slice, clkout_ctrl_div64out_addr, &data);
                data |= 0x4000;  /* SRX_DIV64OUT_EN True */
                status |= cs4224_reg_set_channel(slice, clkout_ctrl_div64out_addr, data);

                /*pfdcdr div by 64 */
                status |= cs4224_reg_get_channel(slice, pfdcdr_clkdiv_ctrl_addr, &data);
                data &= ~0x000f;
                data |= 0x0004;  /* SRX_RDIV_SEL = div by 64 */
                status |= cs4224_reg_set_channel(slice, pfdcdr_clkdiv_ctrl_addr, data);
            }
            
            /* PFD mode on the pfdcdr */
            status |= cs4224_reg_get_channel(slice, clkout_ctrl_refclk_addr, &data);
            data |= 0x8000;  /* SRX_REFCLK_SEL True */
            status |= cs4224_reg_set_channel(slice, clkout_ctrl_refclk_addr, data);

            status |= cs4224_reg_get_channel(slice, rxlockd0_ctrl_addr, &data);
            data |= 0x0001;  /* PD_MODE=0 and FORCE_LOCK=1 */
            status |= cs4224_reg_set_channel(slice, rxlockd0_ctrl_addr, data);

            /* re-synch the elastic stores */
            cs4224_resync_elsto(slice, rxelst0_ctrl_addr);
            cs4224_resync_elsto(slice, txelst0_ctrl_addr);
            cs4224_resync_elsto(slice, txelst0_ctrl_addr_2);
            
            break;
        }

        default:
        {
            CS_PRINTF(("ERROR: Invalid loopback type=%d\n", lb_type));
            cs4224_unlock(slice);
            return CS_ERROR;

        }
    }

    cs4224_unlock(slice);

    CS_UDELAY(5);

    return status;
}

/**
 * Simplex loopbacks are supported on Simplex devices only. This method supports 
 * Simplex loopbacks. Unlike digital loopbacks, simplex loopbacks do not loopback
 * on a port-pair. The two slices seem arbitrary, as can be seen in the following 
 * slice/mate association table.
 *
 * 16 port Simplex CS4224 slice/mate association table: 
 *
 *                          (16-port)  
 *                            CS4224   
 *                  Slice     Mate       Direction 
 *                    0        1     Rx (line to host) 
 *                    1        0     Rx (line to host)
 *                    2        4     Rx (line to host) 
 *                    3        5     Tx (host to line) 
 *                    4        2     Rx (line to host) 
 *                    5        3     Tx (host to line) 
 *                    6        7     Tx (host to line) 
 *                    7        6     Tx (host to line) 
 *                    8       10     Rx (line to host) 
 *                    9       11     Rx (line to host) 
 *                   10        8     Rx (line to host)
 *                   11        9     Rx (line to host)
 *                   12       15     Tx (host to line)
 *                   13       14     Tx (host to line)
 *                   14       13     Tx (host to line)
 *                   15       12     Tx (host to line)
 *
 * As can be seen from the above table, on a 16 port simplex CS4224 device, slice 14 
 * can be loopback to slice 13 or vice-versa.
 *
 * Illustration of the simplex loopback location
 *    
 *                         Line             Host
 *                        +---------------------+
 *                    Tx -+----------<-------+--+- Rx (port 13)
 *                        +------------------|--+
 *                                           |
 *                           +------->-------+
 *                           |
 *                        +--|------------------+
 *                    Tx -+--+-------<----------+- Rx (port 14)
 *                        +---------------------+
 *                  
 * @param slice    [I] - The receive (Rx) slice of the loopback
 * @param enable   [I] - TRUE to enable the loopback or FALSE to disable the loopback
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 *
 */
cs_status cs4224_diags_simplex_loopback_set(
    cs_uint32                              slice,
    cs_uint8                               enable,
    cs4224_diags_simplex_loopback_state_t* state)
{
    cs_status status = CS_OK;
    cs_uint32 mate_slice;
    cs_uint16 data = 0;
    cs_uint16 stx0_misc_addr;
    cs_uint16 rx0_config_addr;
    cs_uint16 rxelst0_addr;
    cs_uint16 txelst0_addr;
    cs_uint16 power_down_addr;     
    cs_uint16 prbs_mseq_spare12;
    cs_uint16 dfe_config;
    cs_uint16 agc_config;

    if (cs4224_is_hw_duplex(slice))
    {
        CS_PRINTF(("ERROR: Simplex loopbacks supported on Simplex devices only\n"));
        return CS_ERROR;
    }

    mate_slice = (slice & 0xffffff00) | g_cs4224_simplex_valid_mate_slice[slice&0xf];

    if (cs4224_line_rx_to_host_tx_dir(slice))
    {
        /* CS_PRINTF(("Rx and Tx slices dir are line rx to host tx\n")); */
        stx0_misc_addr    = CS4224_PP_HOST_SDS_COMMON_STX0_MISC;
        rx0_config_addr   = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG;
        rxelst0_addr      = CS4224_PP_LINE_SDS_COMMON_RXELST0_Control;
        txelst0_addr      = CS4224_PP_HOST_SDS_COMMON_TXELST0_Control;
        power_down_addr   = CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB;
        prbs_mseq_spare12 = CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB;
        dfe_config        = CS4224_PP_LINE_SDS_COMMON_SRX0_DFE_CONFIG;
        agc_config        = CS4224_PP_LINE_SDS_COMMON_SRX0_AGC_CONFIG1;
    }
    else
    {
        /* CS_PRINTF(("Rx and Tx slices dir are host rx to line tx\n")); */
        stx0_misc_addr    = CS4224_PP_LINE_SDS_COMMON_STX0_MISC;
        rx0_config_addr   = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CONFIG;
        rxelst0_addr      = CS4224_PP_HOST_SDS_COMMON_RXELST0_Control;
        txelst0_addr      = CS4224_PP_LINE_SDS_COMMON_TXELST0_Control;
        power_down_addr   = CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB;
        prbs_mseq_spare12 = CS4224_PP_HOST_SDS_DSP_MSEQ_SPARE12_LSB;
        dfe_config        = CS4224_PP_HOST_SDS_COMMON_SRX0_DFE_CONFIG;
        agc_config        = CS4224_PP_HOST_SDS_COMMON_SRX0_AGC_CONFIG1;
    }

    cs4224_lock(slice);
    cs4224_lock(mate_slice);

    if (TRUE == enable)
    {
        /* check to see if simplex loopback already applied */
        if (state->slice_state.initialized)
        {
            CS_PRINTF(("ERROR: Simplex loopback already applied\n"));
            cs4224_unlock(slice);
            cs4224_unlock(mate_slice);
            return CS_ERROR;
        }

        /* CS_PRINTF(("Simplex Loopback, Enable\n"));*/

        /* save context prior to applying loopback to be restored when loopbacks are tore down */
        status = cs4224_diags_simplex_loopback_save_state(slice,      &(state->slice_state));
        status = cs4224_diags_simplex_loopback_save_state(mate_slice, &(state->mate_slice_state));

        status |= cs4224_reg_get_channel(mate_slice, prbs_mseq_spare12, &data);
        data &= ~0x0006; /* disable squelch and power savings */
        status |= cs4224_reg_set_channel(mate_slice, prbs_mseq_spare12, data);

        status |= cs4224_reg_get_channel(slice, prbs_mseq_spare12, &data);
        data &= ~0x0006; /* disable squelch and power savings */
        status |= cs4224_reg_set_channel(slice, prbs_mseq_spare12, data);

        CS_UDELAY(5);

        /* tricle power-up demux */
        status |= cs4224_reg_set_channel(mate_slice, power_down_addr, 0x001f); 
        status |= cs4224_reg_set_channel(slice, power_down_addr, 0x001f); 
        status |= cs4224_reg_set_channel(mate_slice, power_down_addr, 0x0000); 
        status |= cs4224_reg_set_channel(slice, power_down_addr, 0x0000); 

        status |= cs4224_reg_get_channel(mate_slice, rx0_config_addr, &data);
        data |= 0x0001;  /* SRX_LPBK_EN=1 */
        status |= cs4224_reg_set_channel(mate_slice, rx0_config_addr, data);

        status |= cs4224_reg_get_channel(slice, stx0_misc_addr, &data);
        data |= 0x0008; /* STX_LPBK_EN=1 */
        status |= cs4224_reg_set_channel(slice, stx0_misc_addr, data);

        /* enable the DFE path, the simplex loopback requires it */
        status |= cs4224_reg_get_channel(mate_slice, dfe_config, &data);
        data &= ~0x0001; /* SRX_DFE_BYPASS_EN = 0 */
        data = 0x0440;
        status |= cs4224_reg_set_channel(mate_slice, dfe_config, data);

        status |= cs4224_reg_get_channel(mate_slice, agc_config, &data); 
        data |= 0x0001; /* SRX_AGC_ENB_LIMAMP = 1 */
        status |= cs4224_reg_set_channel(mate_slice, agc_config, data); 
    }
    else
    {
        if (!state->slice_state.initialized)
        {
            CS_PRINTF(("ERROR: Simplex loopback not applied\n"));
            cs4224_unlock(slice);
            cs4224_unlock(mate_slice);
            return CS_ERROR;
        }

        /* CS_PRINTF(("Simplex Loopback, Disable\n")); */

        /* restore context to restore data-path to the state is was in prior to applying the loopback */
        status = cs4224_diags_simplex_loopback_restore_state(slice,      &(state->slice_state));
        status = cs4224_diags_simplex_loopback_restore_state(mate_slice, &(state->mate_slice_state));
    }

    /* re-synch the Rx elastic stores */
    cs4224_resync_elsto(slice,      rxelst0_addr);
    cs4224_resync_elsto(mate_slice, rxelst0_addr);

    /* re-synch the Tx elastic stores */
    cs4224_resync_elsto(slice,      txelst0_addr);
    cs4224_resync_elsto(mate_slice, txelst0_addr);

    cs4224_unlock(slice);
    cs4224_unlock(mate_slice);

    CS_UDELAY(5);

    return status;
}

/**
 * This method is called to enable a digital loopback on one of the interfaces 
 * of the device. 
 *
 *
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to loopback. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 *
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_duplex_loopback_enable 
 *   instead.
 */
cs_status cs4224_diags_loopback_enable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf)
{
    cs_status status = CS_OK;
    cs4224_diags_duplex_loopback_state_t* state;

    if (CS4224_LOOPBK_LINE == intf)
    {
        state = &g_cs4224_duplex_loopback_line_state[slice&0x7];
    }
    else
    {
        state = &g_cs4224_duplex_loopback_host_state[slice&0x7];
    }

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  TRUE, 
                  state);
    
    return status;
}


/**
 * This method is called to disable a digital loopback that had previously
 * been applied to an interface of the device.
 * 
 *       instead.
 *
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to disable loopback on. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 *
 * @return CS_OK on success, CS_ERROR on failure
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_duplex_loopback_disable 
 */
cs_status cs4224_diags_loopback_disable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf)
{
    cs_status status = CS_OK;
    cs4224_diags_duplex_loopback_state_t* state;

    if (CS4224_LOOPBK_LINE == intf)
    {
        state = &g_cs4224_duplex_loopback_line_state[slice&0x7];
    }
    else
    {
        state = &g_cs4224_duplex_loopback_host_state[slice&0x7];
    }

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  FALSE, 
                  state);
    
    return status;
}

/**
 * This method is called to enable a digital loopback on one of the interfaces 
 * of the device. 
 *
 *
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to loopback. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_duplex_loopback_enable 
 *   instead.
 */
cs_status cs4224_diags_digital_loopback_enable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf)
{
    cs_status status = CS_OK;
    cs4224_diags_duplex_loopback_state_t* state;

    if (CS4224_LOOPBK_LINE == intf)
    {
        state = &g_cs4224_duplex_loopback_line_state[slice&0x7];
    }
    else
    {
        state = &g_cs4224_duplex_loopback_host_state[slice&0x7];
    }

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  TRUE, 
                  state);
    
    return status;
}


/**
 * This method is called to disable a digital loopback that had previously
 * been applied to an interface of the device.
 * 
 *
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to disable loopback on. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 *
 * @return CS_OK on success, CS_ERROR on failure
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_duplex_loopback_disable 
 *   instead.
 */
cs_status cs4224_diags_digital_loopback_disable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf)
{
    cs_status status = CS_OK;
    cs4224_diags_duplex_loopback_state_t* state;

    if (CS4224_LOOPBK_LINE == intf)
    {
        state = &g_cs4224_duplex_loopback_line_state[slice&0x7];
    }
    else
    {
        state = &g_cs4224_duplex_loopback_host_state[slice&0x7];
    }

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  FALSE, 
                  state);
    
    return status;
}


/**
 * This method is called to enable a duplex loopback on one of the interfaces 
 * of the device. 
 *
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to loopback. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 * @param state   [I] -  A pointer to a structure containg state information
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_duplex_loopback_enable(
        cs_uint32                             slice,
        e_cs4224_loopback                     lb_type,
        e_cs4224_loopback_interface           intf,
        cs4224_diags_duplex_loopback_state_t* state)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  TRUE, 
                  state);
    
    return status;
}


/**
 * This method is called to disable a digital loopback that had previously
 * been applied to an interface of the device.
 * 
 * @param slice   [I] -  The slice to the port of the device to access 
 * @param lb_type [I] -  The interface to disable loopback on. 
 * @param intf    [I] -  The interface or point where the loopback
 *                       will be set
 * @param state   [I] -  A pointer to a structure containg state information
 *
 * @return CS_OK on success, CS_ERROR on failure
 *
 */
cs_status cs4224_diags_duplex_loopback_disable(
        cs_uint32                             slice,
        e_cs4224_loopback                     lb_type,
        e_cs4224_loopback_interface           intf,
        cs4224_diags_duplex_loopback_state_t* state)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_duplex_loopback_set(
                  slice, 
                  lb_type, 
                  intf, 
                  FALSE, 
                  state);
    
    return status;
}


/**
 * This method is called to enable an analog loopback across two slices.
 *
 * @param slice   [I] -  The receive (Rx) slice of the loopback
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_simplex_loopback_enable 
 *   instead.
 */
cs_status cs4224_diags_analog_loopback_enable(
        cs_uint32   slice)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_simplex_loopback_set(
                  slice, 
                  TRUE, 
                  &g_cs4224_simplex_loopback_state[slice&0xf]);
    
    return status;
}


/**
 * This method is called to disable an analog loopback across two slices.
 * 
 * @param slice   [I] -  The receive (Rx) slice of the loopback
 *
 * @return CS_OK on success, CS_ERROR on failure
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_simplex_loopback_disable 
 *   instead.
 */
cs_status cs4224_diags_analog_loopback_disable(
        cs_uint32   slice)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_simplex_loopback_set(
                  slice, 
                  FALSE, 
                  &g_cs4224_simplex_loopback_state[slice&0xf]);
    
    return status;
}

/**
 * This method is called to enable an simplex loopback across two slices.
 *
 * @param slice   [I] -  The receive (Rx) slice of the loopback
 * @param state   [I] -  A pointer to a structure containg state information
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_simplex_loopback_enable(
        cs_uint32                              slice,
        cs4224_diags_simplex_loopback_state_t* state)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_simplex_loopback_set(
                  slice, 
                  TRUE, 
                  state);
    
    return status;
}


/**
 * This method is called to disable an simplex loopback across two slices.
 * 
 * @param slice   [I] -  The receive (Rx) slice of the loopback
 * @param state   [I] -  A pointer to a structure containg state information
 *
 * @return CS_OK on success, CS_ERROR on failure
 */
cs_status cs4224_diags_simplex_loopback_disable(
        cs_uint32                              slice,
        cs4224_diags_simplex_loopback_state_t* state)
{
    cs_status status = CS_OK;

    status |= cs4224_diags_simplex_loopback_set(
                  slice, 
                  FALSE, 
                  state);
    
    return status;
}


#endif /* CS_HAS_DEBUG_LOOPBACKS == 1 */


#if (CS_HAS_DEBUG_PRBS == 1)

/**
 * This method is used in simplex mode to determine which checker
 * is associated with the target slice/channel. 
 *
 * @param slice [I] - The slice or channel of the device to access.
 *
 * @return CS4224_PRBS_LINE_INTERFACE or CS4224_HOST_INTERFACE depending
 *         on which PRBS checker is associated with this channel.
 *
 * @private
 */
e_cs4224_prbs_interface cs4224_diags_prbs_simplex_get_checker(cs_uint32 slice)
{
    if(cs4224_is_hw_simplex(slice))
    {
        if(cs4224_line_rx_to_host_tx_dir(slice))
        {
            return CS4224_PRBS_LINE_INTERFACE;
        }
        else
        {
            return CS4224_PRBS_HOST_INTERFACE;
        }
    }

    /* If it is not simplex just default to the line interface */
    return CS4224_PRBS_LINE_INTERFACE;
}

/**
 * This method is used in simplex mode to determine which generator
 * is associated with the target slice/channel. 
 *
 * @param slice [I] - The slice or channel of the device to access.
 *
 * @return CS4224_PRBS_LINE_INTERFACE or CS4224_HOST_INTERFACE depending
 *         on which PRBS generator is associated with this channel.
 *
 * @private
 */
e_cs4224_prbs_interface cs4224_diags_prbs_simplex_get_generator(cs_uint32 slice)
{
    if(cs4224_is_hw_simplex(slice))
    {
        if(cs4224_line_rx_to_host_tx_dir(slice))
        {
            return CS4224_PRBS_HOST_INTERFACE;
        }
        else
        {
            return CS4224_PRBS_LINE_INTERFACE;
        }
    }

    /* If it is not simplex just default to the line interface */
    return CS4224_PRBS_LINE_INTERFACE;
}

/**
 * This is an internal method used to set the bitswap
 * bit when configuring the PRBS generator or checker.
 * 
 * @param slice    [I] - The slice of the adapter to configure.
 * @param prbs_sel [I] - The PRBS generator or checker
 * @param is_rx    [I] - The RX or the TX direction
 * @param enable   [I] - 1 to set the bit or 0
 *                       to clear it.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @private
 */
cs_status cs4224_diags_prbs_set_bitswap(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              is_rx,
    cs_boolean              enable)
{
    cs_status status = CS_OK;
    cs_uint16 tx_config_addr;
    cs_uint16 rx_config_addr;
    cs_uint16 data = 0;
    
    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            tx_config_addr = CS4224_PP_HOST_SDS_COMMON_TX0_Config;
            rx_config_addr = CS4224_PP_HOST_SDS_COMMON_RX0_Config;

            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            tx_config_addr = CS4224_PP_LINE_SDS_COMMON_TX0_Config;
            rx_config_addr = CS4224_PP_LINE_SDS_COMMON_RX0_Config;
            break;
        }
        default:
        { 
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }

    cs4224_lock(slice);

    if(!is_rx)
    {
        /* Set or clear the bitswap bit for the Tx */
        status |= cs4224_reg_get_channel(slice, tx_config_addr, &data);
        if(enable)
        {
            data |= 0x8;
        }
        else
        {
            data &= ~0x8;
        }
        status |= cs4224_reg_set_channel(slice, tx_config_addr, data);
    }
    else
    {
        /* Set the bitswap bit for the Rx  */
        status |= cs4224_reg_get_channel(slice, rx_config_addr, &data);
        if(enable)
        {
            data |= 0x8;
        }
        else
        {
            data &= ~0x8;
        }
        status |= cs4224_reg_set_channel(slice, rx_config_addr, data);
    }

    cs4224_unlock(slice);

    return status;
}


/**
 * Configure the PRBS generator for transmit 
 *
 * NOTE: Some of the config here cannot be reversed without saving state. To fully
 * reverse the config run cs4224_slice_enter_operational_state to reconfig the slice.
 * 
 * @param slice       [I] -  The slice to the port of the device to access 
 * @param prbs_sel    [I] -  Which of the PRBS generator to configure (LINE/HOST/SPLX)
 * @param polynomial  [I] -  Select the polynomial used to generate the pattern 
 * @param invert      [I] -  TRUE to invert the pattern, FALSE leaves the pattern as is. 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_generator_config(
        cs_uint32                slice,
        e_cs4224_prbs_interface  prbs_sel,
        e_cs4224_prbs_polynomial polynomial,
        cs_uint8                 invert)
{
    /* Any modifications here should go in cs4224_diags_fix_ptrn_generator_cfg as well */
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint16 stx0_misc_addr;
    e_cs4224_mseq_id mseq_id;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    cs4224_lock(slice);
    
    if (CS4224_PRBS_HOST_INTERFACE == prbs_sel)
    {
        stx0_misc_addr       = CS4224_PP_HOST_SDS_COMMON_STX0_MISC;
        prbs_cfg_addr        = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Cfg;
        mseq_id              = CS4224_DPLX_LINE_MSEQ;
    }
    else /* CS4224_PRBS_LINE_INTERFACE */
    {
        stx0_misc_addr       = CS4224_PP_LINE_SDS_COMMON_STX0_MISC;
        prbs_cfg_addr        = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Cfg;
        mseq_id              = CS4224_DPLX_HOST_MSEQ;
    } 

    /* Disable power savings to get the generator to function
     * correctly */
    cs4224_mseq_enable_power_savings(slice, mseq_id, FALSE);

    status |= cs4224_reg_get_channel(slice, stx0_misc_addr, &data);
    data &= ~0x0011; /* power-up mux, STX_EYEMODE_EN=0 */
    status |= cs4224_reg_set_channel(slice, stx0_misc_addr, data);

    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);
    /* Clear and set the polynomial */
    data &= ~0x70;
    data |= ((cs_uint16)polynomial << 4);
    /* Set the invert bit if required */ 
    if(invert)
    {
        data |= 0x4;
    }
    else
    {
        data &= ~0x4;
    }
    /* Clear the fixed pattern enable and the prbs gen enable bits */
    data = CS_CLR(data,0x3);
    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);

    cs4224_unlock(slice);

    return status;
}


/**
 * Enable or disable the PRBS generator.
 *
 *  @param slice     [I] -  The slice to the port of the device to access 
 *  @param prbs_sel  [I] -  The PRBS generator to enable/disable (HOST or LINE) 
 *  @param enable    [I] -  Set to TRUE to enable, FALSE to disable 
 *
 *  @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_generator_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint8                enable)
{
    /* Any modifications here should go in cs4224_diags_fix_ptrn_generator_enable as well */
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint16 tx_cfg_addr;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            prbs_cfg_addr  = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Cfg;
            tx_cfg_addr    = CS4224_PP_HOST_SDS_COMMON_TX0_Config;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            prbs_cfg_addr  = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Cfg;
            tx_cfg_addr    = CS4224_PP_LINE_SDS_COMMON_TX0_Config;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);
    
    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);
    data = CS_CLR(data, 0x3);
    if(enable)
    {
        /* prbs gen enable */
        data |= CS_BIT0;
    }
    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);
    
    if(enable)
    {
        /* Enable bitswap in TX direction */
        status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, FALSE, TRUE);
        
        status |= cs4224_reg_get_channel(slice, tx_cfg_addr, &data);
        data = CS_CLR(data, 0x3);
        /* data_source = PRBS */
        data |= 0x01;
        status |= cs4224_reg_set_channel(slice, tx_cfg_addr, data);

    }
    else
    {
        CS_TRACE(("WARNING: Not all config is rolled back when disabling PRBS generator. Reconfigure slice 0x%x to roll back all config\n",slice));
        
        /* By default bitswap is enabled. Now this is something we need to cache and save
         * outside of the API so that we can roll it back when we disable PRBS generation.
         * For now, just leave this commented out so we don't disable bitswap and we
         * allow traffic to pass through the part.
         */
        /* Disable bitswap in TX direction */
        /*status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, FALSE, FALSE);*/

        status |= cs4224_reg_get_channel(slice, tx_cfg_addr, &data);
        /* data_source = DIG_TX_DIN */
        data = CS_CLR(data, 0x3);
        status |= cs4224_reg_set_channel(slice, tx_cfg_addr, data);
    }

    cs4224_unlock(slice);

    return status;
}

/**
 * This method is used to configure the error insertion attributes
 * of the PRBS generator.
 *
 * @param slice    [I] - The slice of the device to configure error
 *                     injection on.
 * @param prbs_sel [I] - The PRBS interface to inject errors on.
 * @param mode     [I] - The selected error injection mode.
 * @param enable   [I] - TRUE to enable the mode, FALSE to disable it.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_generator_set_error_ctrl(
    cs_uint32                  slice,
    e_cs4224_prbs_interface    prbs_sel,
    e_cs4224_prbsgen_error_cfg mode,
    cs_boolean                 enable)
{
    cs_status status = CS_OK;
    cs_uint32 ctrl_addr = 0;
    cs_uint16 reg_data;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    if(prbs_sel == CS4224_PRBS_LINE_INTERFACE)
    {
        ctrl_addr = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Ctrl;
    }
    else
    {
        ctrl_addr = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Ctrl;
    }

    status |= cs4224_reg_get_channel(slice, ctrl_addr, &reg_data);

    reg_data &= ~mode;

    if(enable)
    {
        reg_data |= mode;
    }

    status |= cs4224_reg_set_channel(slice, ctrl_addr, reg_data);

    return status;
}

/**
 * This is a diagnostic method that may be used to put the PRBS
 * generator in local timing mode in the scenario where an external
 * data source is not available. This mode is intended for debugging
 * purposes and should never be used for qualification/characterization
 * purposes as it can add significant jitter.
 *
 * This method cannot be used on adjacent lanes as it causes significant
 * jitter which will affect the ability to carry traffic. It can only
 * be used on port pairs that are not adjacent.
 *
 * @param slice    [I] - The slice of the device to put into local timing
 *                       mode.
 * @param prbs_sel [I] - The PRBS interface to put into local timing mode.
 * @param enable   [I] - Set to TRUE to enable local timing mode or FALSE
 *                       to disable local timing mode.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_prbs_generator_set_local_timing_mode(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              enable)
{
    return cs4224_diags_prbs_generator_set_pfd_mode(
        slice,
        prbs_sel,
        enable);
}


/**
 * If the PRBS generator is put into PFD mode the microsequencer
 * gets stalled. It does not get un-stalled again if taken out of
 * PFD mode. This would have to be done manually.
 *
 * @param slice    [I] - The slice of the device to put into PFD mode
 * @param prbs_sel [I] - The PRBS interface
 * @param enable   [I] - Set to TRUE to enable PFD mode.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @deprecated This method has been replaced by
 *             cs4224_diags_prbs_generator_set_local_timing_mode() and
 *             should not be used as it may be turned off in future
 *             API releases.
 */
cs_status cs4224_diags_prbs_generator_set_pfd_mode(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              enable)
{
    cs_status status = CS_OK;
    cs_uint32 ctrl_addr = 0;
    cs_uint16 reg_data;
    cs_uint16 power_down_lsb_addr;
    cs_uint16 squelch_addr;
    cs_uint16 mailbox_out_addr, mailbox_in_addr;
    e_cs4224_mseq_id mseq_id;

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    if(prbs_sel == CS4224_PRBS_LINE_INTERFACE)
    {
        ctrl_addr           = CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_CONTROL;
        power_down_lsb_addr = CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB;
        mseq_id             = CS4224_DPLX_HOST_MSEQ;
        squelch_addr        = CS4224_PP_LINE_SDS_COMMON_STX0_SQUELCH;
        mailbox_out_addr    = CS4224_PP_HOST_SDS_DSP_MSEQ_MAIL_OUT_MSB;
        mailbox_in_addr     = CS4224_PP_LINE_SDS_DSP_MSEQ_MAIL_IN_MSB;
    }
    else
    {
        ctrl_addr           = CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_CONTROL;
        power_down_lsb_addr = CS4224_PP_HOST_SDS_DSP_MSEQ_POWER_DOWN_LSB;
        mseq_id             = CS4224_DPLX_LINE_MSEQ;
        squelch_addr        = CS4224_PP_HOST_SDS_COMMON_STX0_SQUELCH;
        mailbox_out_addr    = CS4224_PP_LINE_SDS_DSP_MSEQ_MAIL_OUT_MSB;
        mailbox_in_addr     = CS4224_PP_HOST_SDS_DSP_MSEQ_MAIL_IN_MSB;
    }

    if(enable)
    {
        status |= cs4224_mseq_enable_power_savings(slice, mseq_id, FALSE);

        CS_MDELAY(5);
            
        /* If the microsequencer was running then stall it */
        status |= cs4224_mseq_stall(slice, mseq_id, TRUE);
        
        /* Check the power down register */
        cs4224_reg_get_channel(slice, power_down_lsb_addr, &reg_data);
        
        if((reg_data & 0x100) == 0x100)
        {
            reg_data &= ~0x100; /* power-up generator */
            cs4224_reg_set_channel(slice, power_down_lsb_addr, reg_data);
        }
    }
    status |= cs4224_reg_get_channel(slice, ctrl_addr, &reg_data);

    reg_data &= ~0x1;

    if(enable)
    {
        reg_data |= 0x1;
    }

    status |= cs4224_reg_set_channel(slice, ctrl_addr, reg_data);

    /* clear the out mail box queue in case it has a squelch request in it */
    status |= cs4224_reg_set_channel(slice, mailbox_out_addr, 0);

    /* clear the in mail box queue request */
    status |= cs4224_reg_get_channel(slice, mailbox_in_addr, &reg_data);
    reg_data &= ~0x1000;
    status |= cs4224_reg_set_channel(slice, mailbox_in_addr, reg_data);

    /* we must un-squelch the interface in case the ucode had squelched it*/
    status |= cs4224_reg_set_channel(slice, squelch_addr, 0);

    return status;
}


/**
 * This is a diagnostic method used to squelch the output
 * generated by the PRBS generator. It is for testing purposes
 * only.
 *
 * @param slice    [I] - The slice of the generator to squelch
 * @param prbs_sel [I] - The selected generator to squelch.
 * @param squelch  [I] - TRUE to squelch the output, FALSE
 *                       to un-squelch it.
 *
 * @deprecated This method uses cs4224_squelch_driver internally, you may want to
 *             use that method directly instead.
 */
cs_status cs4224_diags_prbs_generator_squelch(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              squelch)
{
    cs_status status = CS_OK;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    if(prbs_sel == CS4224_PRBS_LINE_INTERFACE)
    {
        status |= cs4224_squelch_driver(slice, CS4224_CFG_LINE_SIDE, squelch);
    }
    else
    {
        status |= cs4224_squelch_driver(slice, CS4224_CFG_HOST_SIDE, squelch);
    }

    return status;
}


/**
 * Configure the PRBS checker for receiving a test pattern and verifying it is correct. 
 * 
 *  @param slice       [I] -  The slice to the port of the device to access 
 *  @param prbs_sel    [I] -  Which PRBS checker to configure (CS4224_PRBS_HOST_INTERFACE, CS4224_PRBS_LINE_INTERFACE)
 *  @param polynomial  [I] -  The polynomial to use to generate output. 
 *  @param invert      [I] -  TRUE to invert the pattern, FALSE leaves the pattern as is. 
 *  @param lbk_enable  [I] -  Unused.
 *
 *  @return CS_OK on success, CS_ERROR on failure
 */
cs_status cs4224_diags_prbs_checker_config(
        cs_uint32                slice,
        e_cs4224_prbs_interface  prbs_sel,
        e_cs4224_prbs_polynomial polynomial,
        cs_uint8                 invert,
        cs_uint8                 lbk_enable)
{
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint16 prbs_ctrl_addr;
    (void)lbk_enable; /* unused, eliminate compiler warning */

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_TRACE(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    cs4224_lock(slice);

    if (CS4224_PRBS_HOST_INTERFACE == prbs_sel)
    {
        prbs_cfg_addr        = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Cfg;
        prbs_ctrl_addr       = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Ctrl;
    }
    else /* CS4224_PRBS_LINE_INTERFACE */
    {
        prbs_cfg_addr        = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Cfg;
        prbs_ctrl_addr       = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Ctrl;
    }

    /* by default, don't enable auto-polarity since it makes it difficult to tell
     * if there are unknown polarity inversions
     */
    data = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Ctrl_dft;
#if 0
    data |= CS_BIT1; /* enable auto polarity detect */
#endif
    status |= cs4224_reg_set_channel(slice, prbs_ctrl_addr, data);

    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);

    /* Clear and set the polynomial */
    data &= ~0x70;
    data |= ((cs_uint16)polynomial << 4);
    
    /* Set the invert bit if required */ 
    if(invert)
    {
        data |= 0x4;
    }
    else
    {
        data &= ~0x4;
    }
    
    /* Disable the checker when reconfiguring as a precaution */
    data &= ~0x1;

    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);

    cs4224_unlock(slice);

    /* Enable bitswap in RX direction */
    status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, TRUE, TRUE);

    return status;
}


/**
 * Enable or disable the PRBS checker.
 * 
 * This method currently disables power savings when the PRBS checker is configured by
 * clearing the LSB of CS4224_PP_MSEQ_SPARE2_LSB. The API currently does not
 * disable power savings when the checker is disabled.
 *
 * @param slice     [I] -  The slice to the port of the device to access 
 * @param prbs_sel  [I] -  Which PRBS checker to enable/disable (HOST or LINE) 
 * @param enable    [I] -  Set to TRUE to enable, FALSE to disable 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_checker_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint8                enable)
{
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint16 prbs_chk_int;
    e_cs4224_mseq_id mseq_id;
    cs_uint32 error_count;

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            prbs_cfg_addr = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Cfg;
            prbs_chk_int  = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_INTERRUPT;
            mseq_id = CS4224_DPLX_HOST_MSEQ;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            prbs_cfg_addr = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Cfg;
            prbs_chk_int  = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_INTERRUPT;
            mseq_id = CS4224_DPLX_LINE_MSEQ;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);

    /* enable/disable the checker */
    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);
    if(enable == TRUE)
    {
        data |= CS_BIT0;
    }
    else
    {
        data &= ~CS_BIT0;
    }
    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);
    
    if(enable == TRUE)
    {
        /* turn off power savings */
        status |= cs4224_mseq_enable_power_savings(slice, mseq_id, FALSE);

        /* Enable bitswap in RX direction */
        status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, TRUE, TRUE);
    }
    else
    {
        /* turn on power savings before we disable the checker */
        status |= cs4224_mseq_enable_power_savings(slice,mseq_id, TRUE);
        
        /* Disable bitswap in RX direction */
        status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, TRUE, FALSE);
    }

    /* clear interrupt status register */
    status |= cs4224_reg_set_channel(slice, prbs_chk_int, 0xffff);
    
    /* clear the counter */
    status |= cs4224_diags_prbs_checker_get_errors(slice, prbs_sel, &error_count);

    cs4224_unlock(slice);

    return status;
}

/**
 * Enable or disable the PRBS checker auto-polarity feature.
 *
 * The auto-polarity feature will compensate for polarity inversions (P/N)
 * in the incoming signal by automatically determining the polarity. Use
 * cs4224_diags_prbs_checker_get_polarity to determine if an inversion was
 * detected
 * 
 * @{note,
 * NOTE: This method must be called after setting up the checker with 
 * cs4224_diags_prbs_checker_config and cs4224_diags_prbs_checker_enable. If
 * called before those methods then the auto-polarity feature will be disabled.
 * }
 *
 * @param slice     [I] -  The slice to the port of the device to access
 * @param prbs_sel  [I] -  Which PRBS checker to configure (HOST or LINE)
 * @param enable    [I] -  Set to TRUE to enable, FALSE to disable
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_checker_autopol_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              enable)
{
    cs_status status = CS_OK;
    cs_uint16 prbs_ctrl = 0;
    cs_uint16 data = 0;

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            prbs_ctrl = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Ctrl;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            prbs_ctrl = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Ctrl;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);


    status |= cs4224_reg_get_channel(slice, prbs_ctrl, &data);
    data &= ~0x1C; /* clear auto-polarity options */
    data |= 0xC; /* set threshold */
    if(enable)
    {
        data |= CS_BIT1;
    }
    else
    {
        data &= ~CS_BIT1;
    }
    status |= cs4224_reg_set_channel(slice, prbs_ctrl, data);

    return status;
}

/**
 * Check the inverted status of the auto-polarity feature. Must have auto-polarity
 * enabled in order for check to be valid (use cs4224_diags_prbs_checker_autopol_enable
 * to enable).
 *
 * @param slice     [I] -  The slice to the port of the device to access
 * @param prbs_sel  [I] -  Which PRBS checker to configure (HOST or LINE)
 * @param inverted  [O] -  Set to TRUE if signal is inverted, FALSE otherwise
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_checker_get_polarity(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              *inverted)
{
    cs_status status = CS_OK;
    cs_uint16 ints = 0;
    cs_uint16 data = 0;

    *inverted = FALSE;

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            ints = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_INTSTATUS;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            ints = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_INTSTATUS;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);


    status |= cs4224_reg_get_channel(slice, ints, &data);
    if(data & CS_BIT2)
    {
        *inverted = TRUE;
    }
    else
    {
        *inverted = FALSE;
    }

    return status;
}

/**
 * Retrieves the 32 bit error count reported by the PRBS checker. 
 *
 * @param slice        [I] -  The slice to the port of the device to access 
 * @param prbs_sel     [I] -  Which PRBS checker to enable/disable (CS4224_PRBS_HOST_INTERFACE, CS4224_PRBS_LINE_INTERFACE) 
 * @param error_count  [O] -  The number of errors dected by the PRBS checker. 
 *
 * @return CS_OK on success, CS_ERROR on failure
 */
cs_status cs4224_diags_prbs_checker_get_errors(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint32*              error_count)
{
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_chk_count0_addr;
    cs_uint16 prbs_chk_count1_addr;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    /* Determine the addresses of the error count registers based
     * on which PRBS is selected */
    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            prbs_chk_count0_addr = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Count0;
            prbs_chk_count1_addr = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_Count1;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            prbs_chk_count0_addr = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count0;
            prbs_chk_count1_addr = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count1;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);
            
    status |= cs4224_reg_get_channel(slice, prbs_chk_count1_addr, &data);
    *error_count = (cs_uint32)data << 16;

    status |= cs4224_reg_get_channel(slice, prbs_chk_count0_addr, &data);
    *error_count |= (cs_uint32)data;

    cs4224_unlock(slice);

    return status;
}




/**
 * This method is called to retrieve the full status of the PRBS checker
 * including the error count, sync status, lock detect
 *
 * @param slice       [I] - The slice/channel of the device to access.
 * @param prbs_sel    [I] - The PRBS checker to access
 * @param error_count [O] - The PRBS error count (0 if there are no errors)
 * @param prbs_sync   [O] - TRUE if the PRBS checker is enabled and synced.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_prbs_checker_get_status(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint32*              error_count,
        cs_boolean*             prbs_sync)
{
    cs_uint32 sync_addr = 0;
    cs_uint16 reg_data = 0;
    cs_status status = CS_OK;

    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_checker(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    if(prbs_sel == CS4224_PRBS_LINE_INTERFACE)
    {
        sync_addr = CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_INTSTATUS;
    }
    else
    {
        sync_addr = CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_INTSTATUS;
    }

    /* Read the sync status */
    status |= cs4224_reg_get_channel(slice, sync_addr, &reg_data);
    
    /* 0 in the PRBS_SYNCs field means synced */
    if(0x0 == (reg_data & 0x1))
    {
        *prbs_sync = TRUE;
    }
    else
    {
        *prbs_sync = FALSE;
    }

    /* Lookup the error count */
    status |= cs4224_diags_prbs_checker_get_errors(slice, prbs_sel, error_count);

    return status;
}


/**
 * This method is called to configure the pattern that the fix pattern generator 
 * transmits. 
 *
 * NOTE: Some of the config here cannot be reversed without saving state. To fully
 * reverse the config run cs4224_slice_enter_operational_state to reconfig the slice.
 * 
 * @param slice       [I] - The slice/channel of the device to access 
 * @param gen_sel     [I] - Which fixed pattern generator to configure (LINE/HOST/SPLX)
 * @param sequence_a  [I] - The bits of sequence A to generate
 * @param repeat_a    [I] - The number of times to repeat sequence A before switching to sequence B. 
 *     
 * @param sequence_b  [I] - The bits of sequence B to generate
 * @param repeat_b    [I] - The number of times to repeat sequence B before switching back to sequence A. 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_fix_ptrn_generator_cfg(
        cs_uint32               slice,
        e_cs4224_prbs_interface gen_sel,
        cs_uint32               sequence_a,
        cs_uint8                repeat_a,
        cs_uint32               sequence_b,
        cs_uint8                repeat_b)
{
    /* based heavily on cs4224_diags_prbs_generator_config, any modifications here should also go there */
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint32 prbs_ptrn_addr;
    cs_uint16 stx0_misc_addr;
    e_cs4224_mseq_id mseq_id;

    if(gen_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            gen_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    if (CS4224_PRBS_HOST_INTERFACE == gen_sel)
    {
        prbs_cfg_addr        = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Cfg;
        prbs_ptrn_addr       = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Fixed0_Pattern1;
        stx0_misc_addr       = CS4224_PP_HOST_SDS_COMMON_STX0_MISC;
        mseq_id              = CS4224_DPLX_LINE_MSEQ;
    }
    else /* CS4224_PRBS_LINE_INTERFACE */
    {
        prbs_cfg_addr        = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Cfg;
        prbs_ptrn_addr       = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Fixed0_Pattern1;
        stx0_misc_addr       = CS4224_PP_LINE_SDS_COMMON_STX0_MISC;
        mseq_id              = CS4224_DPLX_HOST_MSEQ;
    }
    cs4224_lock(slice);

    /* Disable power savings to get the generator to function correctly */
    cs4224_mseq_enable_power_savings(slice, mseq_id, FALSE);

    status |= cs4224_reg_get_channel(slice, stx0_misc_addr, &data);
    data &= ~0x0011; /* power-up mux, STX_EYEMODE_EN=0 */
    status |= cs4224_reg_set_channel(slice, stx0_misc_addr, data);

    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);
    /* Clear the fixed pattern enable and the prbs gen enable bits */
    data = CS_CLR(data,0x3);
    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);

    /* Setup the pattern. The register addresses are based on the
     * location of the PRBSGEN0_Fixed0_Pattern1 register.
     *
     * The most significant
     * bits go into the Fixed0_Pattern1 register and the least significant
     * bits go in the Fixed0_Pattern0 register. */
    status |= cs4224_reg_set_channel(slice, prbs_ptrn_addr, (sequence_a >> 16) & 0xFFFF);
    status |= cs4224_reg_set_channel(slice, prbs_ptrn_addr+1, (sequence_a) & 0xFFFF);

    status |= cs4224_reg_set_channel(slice, prbs_ptrn_addr+2, (sequence_b >> 16) & 0xFFFF);
    status |= cs4224_reg_set_channel(slice, prbs_ptrn_addr+3, (sequence_b) & 0xFFFF);
    
    /* Setup the repeat register */
    status |= cs4224_reg_set_channel(slice, prbs_ptrn_addr+4, ((cs_uint16)repeat_b << 8) | repeat_a); 

    cs4224_unlock(slice);
    
    return status;
}


/**
 * Enable or disable the fixed pattern generator 
 *
 * @param slice     [I] - The slice to the port of the device to access 
 * @param prbs_sel  [I] - Which fixed pattern generator to enable/disable (HOST or LINE) 
 * @param enable    [I] - Set to TRUE to enable, FALSE to disable 
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_fix_ptrn_generator_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              enable)
{
    /* based heavily on cs4224_diags_prbs_generator_enable, any modifications here should also go there */
    cs_status status = CS_OK;
    cs_uint16 data;
    cs_uint16 prbs_cfg_addr;
    cs_uint16 tx_cfg_addr;
    
    if(prbs_sel == CS4224_PRBS_SIMPLEX_INTERFACE)
    {
        if(cs4224_is_hw_simplex(slice))
        {
            prbs_sel = cs4224_diags_prbs_simplex_get_generator(slice);
        }
        else
        {
            /* undefined in duplex mode */
            CS_PRINTF(("ERROR: CS4224_PRBS_SIMPLEX_INTERFACE available in simplex mode only\n"));
            return CS_ERROR;
        }
    }

    switch(prbs_sel)
    {
        case CS4224_PRBS_HOST_INTERFACE:
        {
            prbs_cfg_addr  = CS4224_PP_HOST_SDS_COMMON_PRBSGEN0_Cfg;
            tx_cfg_addr    = CS4224_PP_HOST_SDS_COMMON_TX0_Config;
            break;
        }
        case CS4224_PRBS_LINE_INTERFACE:
        {
            prbs_cfg_addr  = CS4224_PP_LINE_SDS_COMMON_PRBSGEN0_Cfg;
            tx_cfg_addr    = CS4224_PP_LINE_SDS_COMMON_TX0_Config;
            break;
        }
        default:
        {
            CS_PRINTF(("ERROR: Invalid prbs_sel=%d\n", prbs_sel));
            return CS_ERROR;
        }
    }
    cs4224_lock(slice);
    
    status |= cs4224_reg_get_channel(slice, prbs_cfg_addr, &data);
    data = CS_CLR(data, 0x3);
    if(enable)
    {
        /* fixed pattern enable */
        data |= CS_BIT1;
    }
    status |= cs4224_reg_set_channel(slice, prbs_cfg_addr, data);
    
    if(enable)
    {
        /* Enable bitswap in TX direction */
        status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, FALSE, TRUE);
        
        status |= cs4224_reg_get_channel(slice, tx_cfg_addr, &data);
        data = CS_CLR(data, 0x3);
        /* data_source = PRBS */
        data |= 0x01;
        status |= cs4224_reg_set_channel(slice, tx_cfg_addr, data);

    }
    else
    {
        CS_TRACE(("WARNING: Not all config is rolled back when disabling PRBS generator. Reconfigure slice 0x%x to roll back all config\n",slice));
        
        /* Bitswap is enabled by default, so leave it on here so we can pass traffic after
         * disabling the generator */
        /* Disable bitswap in TX direction */
        /*status |= cs4224_diags_prbs_set_bitswap(slice, prbs_sel, FALSE, FALSE);*/

        status |= cs4224_reg_get_channel(slice, tx_cfg_addr, &data);
        /* data_source = DIG_TX_DIN */
        data = CS_CLR(data, 0x3);
        status |= cs4224_reg_set_channel(slice, tx_cfg_addr, data);
    }

    cs4224_unlock(slice);

    return status;
}

#endif /* CS_HAS_DEBUG_PRBS == 1 */


#if (CS_HAS_DEBUG_STATUS_DUMPS == 1)

/**
 * This is method used to display the current duplex switch state.
 * 
 * @pre
 * +-----------+------------------+-------------------------+------------------+
 * |           | Host             | Switch State            | Line             |
 * | Slice     | Driver Settings  | S=Sqlch,L=lock,E=EdcCvg | Driver Settings  |
 * |           |                  | HL=HiLtncy,LL=LowLtncy  |                  |
 * +-----------+------------------+-------------------------+------------------+
 * |  0        |                  | Disabled                |                  |
 * |  1        |                  | Disabled                |                  |
 * +-----------+------------------+-------------------------+------------------+
 * |  2        |                  | Disabled                |                  |
 * |  3        |                  | Disabled                |                  |
 * +-----------+------------------+-------------------------+------------------+
 * |  4        | CX1    +Running  | Host    (2x2)LL    Line | CX1    +Running  |
 * |           | TX = 0814,  4    |  ... <----> <----> ...  | TX = 0814,  4    |
 * |  5        | CX1    +Running  |            X            | CX1    +Running  |
 * |           | TX = 0814,  4    |  ... <----> <----> ...  | TX = 0814,  4    |
 * +-----------+------------------+-------------------------+------------------+
 * |  6        |                  | Disabled                |                  |
 * |  7        |                  | Disabled                |                  |
 * +-----------+------------------+-------------------------+------------------+
 * 
 * @param slice [I] - A slice on the device to access, only uses the upper bits
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_switch_show_state(
    cs_uint32 slice)
{
    cs_status status = CS_OK;
    e_cs4224_switch_action_t switch_mode;
    e_cs4224_edc_mode        line_edc_mode_0, host_edc_mode_0;
    cs_uint16                line_edc_conv_0, host_edc_conv_0;
    cs_uint16                line_lock_0, host_lock_0;
    cs_uint16                line_squelch_0, host_squelch_0;
    cs_uint16                line_ctrla_0, host_ctrla_0;
    cs_uint16                line_ctrlb_0, host_ctrlb_0;
    cs_boolean               line_mseq_stalled_0, host_mseq_stalled_0;
    cs_uint16                line_clkdiv_ctrl, host_clkdiv_ctrl;
    cs_boolean               low_latency_mode;
    cs_uint32                i, slice_num;

    CS_PRINTF(("+-----------+------------------+-------------------------+------------------+\n"));
    CS_PRINTF(("|           | HostRX + HostTX  | Switch State            | LineRX + LineTX  |\n"));
    CS_PRINTF(("| Slice     |                  | S=Sqlch,L=Lock,E=EdcCvg |                  |\n"));
    CS_PRINTF(("|           |                  | HL=HiLtncy,LL=LowLtncy  |                  |\n"));
    CS_PRINTF(("+-----------+------------------+-------------------------+------------------+\n"));
                
    for (i = 0; i < CS4224_MAX_NUM_SLICES(slice); i++)
    {
        slice_num = (slice & ~0xf) + i;

        /* This method can be called to query the current switch state*/
        status = cs4224_switch_query_mode(slice_num, &switch_mode, &low_latency_mode);

        /* get the EDC converged states */
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_LINE_SDS_DSP_MSEQ_STATUS, &line_edc_conv_0);
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_HOST_SDS_DSP_MSEQ_STATUS, &host_edc_conv_0);
        
        /* get the VCO lock state */
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS, &line_lock_0);
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTSTATUS, &host_lock_0);
        
        /* get the squelch state */
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_LINE_SDS_COMMON_STX0_SQUELCH, &line_squelch_0);
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_HOST_SDS_COMMON_STX0_SQUELCH, &host_squelch_0);
        
        /* get the EDC mode */
        status |= cs4224_query_edc_mode(slice_num,   CS4224_DPLX_LINE_MSEQ, &line_edc_mode_0);
        status |= cs4224_query_edc_mode(slice_num,   CS4224_DPLX_HOST_MSEQ, &host_edc_mode_0);

        /* get the ctrla values */
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_LINE_SDS_COMMON_STX0_TX_OUTPUT_CTRLA, &line_ctrla_0);
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_HOST_SDS_COMMON_STX0_TX_OUTPUT_CTRLA, &host_ctrla_0);

        /* get the ctrlb values */
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_LINE_SDS_COMMON_STX0_TX_OUTPUT_CTRLB, &line_ctrlb_0);
        status |= cs4224_reg_get_channel(slice_num,   CS4224_PP_HOST_SDS_COMMON_STX0_TX_OUTPUT_CTRLB, &host_ctrlb_0);

        /* find out if the microsequencer is stalled */
        status |= cs4224_query_mseq_is_stalled(slice_num,   CS4224_DPLX_LINE_MSEQ, &line_mseq_stalled_0);
        status |= cs4224_query_mseq_is_stalled(slice_num,   CS4224_DPLX_HOST_MSEQ, &host_mseq_stalled_0);

        /* find out the clkdiv ctrl */
        status |= cs4224_reg_get_channel(slice_num, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, &line_clkdiv_ctrl);
        status |= cs4224_reg_get_channel(slice_num, CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL, &host_clkdiv_ctrl);
        
        CS_PRINTF(("|  %d        | RX:", i));
        
        /* Host side */

        if      (host_edc_mode_0 == CS_HSIO_EDC_MODE_SR)       {CS_PRINTF(("SR     "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_CX1)      {CS_PRINTF(("CX1    "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_ZR)       {CS_PRINTF(("ZR     "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_DWDM)     {CS_PRINTF(("DWDM   "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_10G_BP)   {CS_PRINTF(("10G_BP "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_15G_BP)   {CS_PRINTF(("15G_BP "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_FCAN)     {CS_PRINTF(("FCAN   "));}
        else if (host_edc_mode_0 == CS_HSIO_EDC_MODE_DISABLED) {CS_PRINTF(("DISABL "));}
        else                                                   {CS_PRINTF(("?????? "));}
        
        if (host_mseq_stalled_0 == TRUE) {CS_PRINTF(("+Stall"));}
        else                             {CS_PRINTF(("+Run  "));}

        if ((i & 1) == 0)
        {
            if (low_latency_mode == FALSE)
            {
                if      (switch_mode == CS4224_SWITCH_DUPLEX_SWITCH_2x2)       {CS_PRINTF((" | Host    (2x2)HL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_0) {CS_PRINTF((" | Host    (0_0)HL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_1) {CS_PRINTF((" | Host    (0_1)HL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_0) {CS_PRINTF((" | Host    (1_0)HL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_1) {CS_PRINTF((" | Host    (1_1)HL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DISABLE)                 {CS_PRINTF((" | Host     (OFF)     Line | "));}
            }
            else
            {
                if      (switch_mode == CS4224_SWITCH_DUPLEX_SWITCH_2x2)       {CS_PRINTF((" | Host    (2x2)LL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_0) {CS_PRINTF((" | Host    (0_0)LL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_1) {CS_PRINTF((" | Host    (0_1)LL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_0) {CS_PRINTF((" | Host    (1_0)LL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_1) {CS_PRINTF((" | Host    (1_1)LL    Line | "));}
                else if (switch_mode == CS4224_SWITCH_DISABLE)                 {CS_PRINTF((" | Host     (OFF)     Line | "));}
            }
        }
        else
        {
            if      (switch_mode == CS4224_SWITCH_DUPLEX_SWITCH_2x2)       {CS_PRINTF((" |            X            | "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_0) {CS_PRINTF((" |            \\            | "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_1) {CS_PRINTF((" |            \\            | "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_0) {CS_PRINTF((" |            /            | "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_1) {CS_PRINTF((" |            /            | "));}
            else                                                           {CS_PRINTF((" |           n/a           | "));}
        }
        
        /* Line side */
        CS_PRINTF(("RX:"));
        
        if      (line_edc_mode_0 == CS_HSIO_EDC_MODE_SR)       {CS_PRINTF(("SR     "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_CX1)      {CS_PRINTF(("CX1    "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_ZR)       {CS_PRINTF(("ZR     "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_DWDM)     {CS_PRINTF(("DWDM   "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_10G_BP)   {CS_PRINTF(("10G_BP "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_15G_BP)   {CS_PRINTF(("15G_BP "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_FCAN)     {CS_PRINTF(("FCAN   "));}
        else if (line_edc_mode_0 == CS_HSIO_EDC_MODE_DISABLED) {CS_PRINTF(("DISABL "));}
        else                                                   {CS_PRINTF(("?????? "));}
        
        if (line_mseq_stalled_0 == TRUE) {CS_PRINTF(("+Stall |"));}
        else                             {CS_PRINTF(("+Run   |"));}
        
        CS_PRINTF(("\n| "));
        
        if(0x3 == (line_clkdiv_ctrl >> 4 & 0x7))
        {
            CS_PRINTF(("L:/8 "));
        }
        else
        {
            CS_PRINTF(("L:/1 "));
        }
        
        if(0x3 == (host_clkdiv_ctrl >> 4 & 0x7))
        {
            CS_PRINTF(("H:/8"));
        }
        else
        {
            CS_PRINTF(("H:/1"));
        }

        CS_PRINTF((" | TX:A=%04x,B=%04x |  ", host_ctrla_0, host_ctrlb_0));
        
        if (host_squelch_0 == 1)    {CS_PRINTF(("S"));}
        else                        {CS_PRINTF(("."));}
        if (host_lock_0 == 0x41)    {CS_PRINTF(("L"));}
        else                        {CS_PRINTF(("."));}
        if (host_edc_conv_0 & 0x20) {CS_PRINTF(("E"));}
        else                        {CS_PRINTF(("."));}
        
        if ((i & 1) == 0)
        {
            if      (switch_mode == CS4224_SWITCH_DUPLEX_SWITCH_2x2)       {CS_PRINTF((" <----> <----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_0) {CS_PRINTF((" <----> <----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_1) {CS_PRINTF((" <----> -----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_0) {CS_PRINTF(("        <----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_1) {CS_PRINTF(("        -----> "));}
            else                                                           {CS_PRINTF((" <-----------> "));}
        }
        else
        {
            if      (switch_mode == CS4224_SWITCH_DUPLEX_SWITCH_2x2)       {CS_PRINTF((" <----> <----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_0) {CS_PRINTF(("        -----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_0_to_1) {CS_PRINTF(("        <----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_0) {CS_PRINTF((" <----> -----> "));}
            else if (switch_mode == CS4224_SWITCH_DUPLEX_BROADCAST_1_to_1) {CS_PRINTF((" <----> <----> "));}
            else                                                           {CS_PRINTF((" <-----------> "));}
        } 
        if (line_squelch_0 == 1)    {CS_PRINTF(("S"));}
        else                        {CS_PRINTF(("."));}
        if (line_lock_0 == 0x41)    {CS_PRINTF(("L"));}
        else                        {CS_PRINTF(("."));}
        if (line_edc_conv_0 & 0x20) {CS_PRINTF(("E"));}
        else                        {CS_PRINTF(("."));}
        
        CS_PRINTF(("  | TX:A=%04x,B=%04x |\n", line_ctrla_0, line_ctrlb_0));
        
        if ((i & 1) == 1)
        {
            CS_PRINTF(("+-----------+------------------+-------------------------+------------------+\n"));
        }
    }
    return status;
}


/**
 *
 * This method is called to display the VCO lock status on all interfaces
 * of an ASIC.
 *
 * @param slice     [I] - The slice to the port of the device to access 
 * @param prefix    [I] - The prefix string to prepend to the VCO status
 *                        report.
 *
 * Note that this method assumes the Alternate Coarse Tuning (ACT) algorithm
 * is used.
 *
 */
void cs4224_diags_show_vco_status_prefixed(
    cs_uint32   slice,
    const char* prefix)
{
    cs_uint16  line_lock_status,  host_lock_status;
    cs_uint16  line_altct_status, host_altct_status;
    cs_uint8   phy;

    CS_PRINTF(("%s+---------------------------+\n", prefix));
    CS_PRINTF(("%s| VCO Lock Status           |\n", prefix));
    CS_PRINTF(("%s+-----+----------+----------+\n", prefix));
    CS_PRINTF(("%s| Phy | Line FLT | Host FLT |\n", prefix));
    CS_PRINTF(("%s+-----+----------+----------+\n", prefix));
 
    for (phy=0; phy < CS4224_MAX_NUM_SLICES(slice); phy++)
    {
        slice = (slice & 0xffffff00) | phy;

        cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS,  &line_lock_status); 
        cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXVCO0_ALTCT_STATUS, &line_altct_status); 

        cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTSTATUS,  &host_lock_status); 
        cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXVCO0_ALTCT_STATUS, &host_altct_status); 

        if (cs4224_is_hw_simplex(slice))
        {
            if (cs4224_line_rx_to_host_tx_dir(slice))
            {
                CS_PRINTF(("%s|  %2d | (Rx) %s%s%s | (Rx) %s%s%s |\n",  
                  prefix,
                  phy, (line_lock_status  & 0x0040)? "1": "0", 
                       (line_lock_status  & 0x0001)? "1": "0", 
                       (line_altct_status & 0x8000)? "1": "0",
                       "-", "-", "-"));
            }
            else
            {
                CS_PRINTF(("%s|  %2d | (Rx) %s%s%s | (Rx) %s%s%s |\n",  
                  prefix,
                  phy, "-", "-", "-",   
                       (host_lock_status  & 0x0040)? "1": "0", 
                       (host_lock_status  & 0x0001)? "1": "0", 
                       (host_altct_status & 0x8000)? "1": "0"));
            }
        }
        else /* duplex */
        {
            CS_PRINTF(("%s|  %2d | (Rx) %s%s%s | (Rx) %s%s%s |\n",  
              prefix,
              phy, (line_lock_status  & 0x0040)? "1": "0", 
                   (line_lock_status  & 0x0001)? "1": "0", 
                   (line_altct_status & 0x8000)? "1": "0",
                   (host_lock_status  & 0x0040)? "1": "0", 
                   (host_lock_status  & 0x0001)? "1": "0", 
                   (host_altct_status & 0x8000)? "1": "0"));
        }  
    }

    CS_PRINTF(("%s+-----+----------+----------+\n",prefix));

    CS_PRINTF(("%sColumns: F is Lock Debounce Filter, 0=No, 1=Yes\n",prefix)); 
    CS_PRINTF(("%s         L is VCO Lock, 0=No, 1=Yes\n",prefix));
    CS_PRINTF(("%s         T is Coarse Tuning Freq, 0=Saturated, 1=Good\n",prefix));
    if (cs4224_is_hw_simplex(slice))
    {
        CS_PRINTF(("%s         - is not applicable\n",prefix));
    }
}

/**
 *
 * This method is called to display the VCO lock status on all interfaces
 * of an ASIC.
 *
 * @param slice     [I] - The slice to the port of the device to access 
 *
 * Note that this method assumes the Alternate Coarse Tuning (ACT) algorithm
 * is used.
 *
 */
void cs4224_diags_show_vco_status(
    cs_uint32 slice)
{
    cs4224_diags_show_vco_status_prefixed(slice, "");
}

/**
 *
 * This method is called to display the VCO lock status on all interfaces.
 *
 * Note that this method assumes the Alternate Coarse Tuning (ACT) algorithm
 * is used.
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_show_vco_status 
 *   instead.
 */
void cs4224_diags_show_vco_lock_status(void)
{
    cs4224_diags_show_vco_status(0);
}

/**
 *
 * This method is called to return a string pointer argument containing the status
 * of all the VCO lock status on all interfaces of an ASIC. The format of the string pointer is
 * similar to that which is displayed when calling the cs4224_diags_show_vco_lock_status method.
 *
 * @param slice     [I] - The slice to the port of the device to access 
 * @param buffer    [O] - Pointer to a buffer containing dump of lock status
 * 
 * Note that this method assumes the Alternate Coarse Tuning (ACT) algorithm
 * is used.
 *
 * Note that this method will overwrite buffer
 * 
 * @return Pointer to buffer
 *
 */
const char* cs4224_diags_get_vco_status_string(
    cs_uint32 slice,
    char*     buffer) 
{
    cs_uint16  line_lock_status,  host_lock_status;
    cs_uint16  line_altct_status, host_altct_status;
    cs_uint8   phy;
    char       phy_str[3] = {0,0,0};

    /* init buffer before using strcat */
    buffer[0] = 0;

    CS_STRCAT(buffer, "\n");
    CS_STRCAT(buffer, "+---------------------------+\n");
    CS_STRCAT(buffer, "| VCO Lock Status           |\n");
    CS_STRCAT(buffer, "+-----+----------+----------+\n");
    CS_STRCAT(buffer, "| Phy | Line FLT | Host FLT |\n");
    CS_STRCAT(buffer, "+-----+----------+----------+\n");
 
    for (phy=0; phy < CS4224_MAX_NUM_SLICES(slice); phy++)
    {
        slice = (slice & 0xffffff00) | phy;

        cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS,  &line_lock_status); 
        cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXVCO0_ALTCT_STATUS, &line_altct_status); 

        cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTSTATUS,  &host_lock_status); 
        cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXVCO0_ALTCT_STATUS, &host_altct_status); 

        if (phy < 10)
        {
            phy_str[0] = ' ';
            phy_str[1] = phy + '0';
        }
        else
        {
            phy_str[0] = '1';
            phy_str[1] = (phy - 10) + '0';
        }

        if (cs4224_is_hw_simplex(slice))
        {
            if (cs4224_line_rx_to_host_tx_dir(slice))
            {
                CS_STRCAT(buffer, "|  ");
                CS_STRCAT(buffer, phy_str);
                CS_STRCAT(buffer, " | (Rx) " );
                CS_STRCAT(buffer, (line_lock_status  & 0x0040)? "1": "0");
                CS_STRCAT(buffer, (line_lock_status  & 0x0001)? "1": "0");
                CS_STRCAT(buffer, (line_altct_status & 0x8000)? "1": "0");
                CS_STRCAT(buffer, " | (Rx) ");
                CS_STRCAT(buffer, "-");
                CS_STRCAT(buffer, "-");
                CS_STRCAT(buffer, "- |\n");
            }
            else
            {
                CS_STRCAT(buffer, "|  ");
                CS_STRCAT(buffer, phy_str);
                CS_STRCAT(buffer, " | (Rx) " );
                CS_STRCAT(buffer, "-");
                CS_STRCAT(buffer, "-");
                CS_STRCAT(buffer, "-");
                CS_STRCAT(buffer, " | (Rx) ");
                CS_STRCAT(buffer, (host_lock_status  & 0x0040)? "1": "0");
                CS_STRCAT(buffer, (host_lock_status  & 0x0001)? "1": "0");
                CS_STRCAT(buffer, (host_altct_status & 0x8000)? "1 |\n": "0 |\n");
            }
        }
        else /* duplex */
        {
            CS_STRCAT(buffer, "|  ");
            CS_STRCAT(buffer, phy_str);
            CS_STRCAT(buffer, " | (Rx) " );
            CS_STRCAT(buffer, (line_lock_status  & 0x0040)? "1": "0");
            CS_STRCAT(buffer, (line_lock_status  & 0x0001)? "1": "0");
            CS_STRCAT(buffer, (line_altct_status & 0x8000)? "1": "0");
            CS_STRCAT(buffer, " | (Rx) ");
            CS_STRCAT(buffer, (host_lock_status  & 0x0040)? "1": "0");
            CS_STRCAT(buffer, (host_lock_status  & 0x0001)? "1": "0");
            CS_STRCAT(buffer, (host_altct_status & 0x8000)? "1 |\n": "0 |\n");
        }  
    }

    CS_STRCAT(buffer, "+-----+----------+----------+\n");

    CS_STRCAT(buffer, "Columns: F is Lock Debounce Filter, 0=No, 1=Yes\n"); 
    CS_STRCAT(buffer, "         L is VCO Lock, 0=No, 1=Yes\n");
    CS_STRCAT(buffer, "         T is Coarse Tuning Freq, 0=Saturated, 1=Good\n");
    if (cs4224_is_hw_simplex(slice))
    {
        CS_STRCAT(buffer, "         - is not applicable\n");
    }
    
    return buffer;
}

/**
 *
 * This method is called to return a string pointer argument containing the status
 * of all the VCO lock status on all interfaces of an ASIC. The format of the string pointer is
 * similar to that which is displayed when calling the cs4224_diags_show_vco_lock_status method.
 *
 * @param buffer    [O] - Pointer to a buffer containing dump of lock status
 *
 *
 * Note that this method assumes the Alternate Coarse Tuning (ACT) algorithm
 * is used.
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_get_vco_status_string 
 *   instead.
 *
 */
void cs4224_diags_get_vco_lock_status_string(
    char* buffer) 
{
    cs4224_diags_get_vco_status_string(0, buffer);
}


/* $if : CORTINA : Only for regression */
/**
 * Simple wrapper for regression environment. Note this returns a pointer to
 * static mem, and only one buffer is ever used, so multiple calls will overwrite
 * this buffer. We don't care though, just for testing
 * 
 * @param slice [I] - Slice to get the VCO status from (line & host)
 * 
 * @return VCO status string
 */
char* cs4224_diags_get_vco_status_string_wrapper(
    cs_uint32 slice)
{
    static char buffer[800];

    cs4224_diags_get_vco_lock_status_string(buffer);

    return buffer;
}
/* $endif : CORTINA */

/**
 *
 * This method is called to return the VCO lock status on one simplex or
 * two duplex VCOs. The receiver VCO lock status(s) are returned in the 
 * vco argument pointer. 
 * 
 * Note that on a simplex slice, both the line and host structure elements
 * will be set to the VCO lock status regardless of the direction.
 *
 * @param slice  [I] - The slice to the port of the device to access 
 * @param vco    [O] - A structure contining the status of the VCO lock(s)
 *
 * @deprecated Use cs4224_query_link_ready, cs4224_query_links_ready,
 * cs4224_wait_for_link_ready, cs4224_wait_for_links_ready
 * 
 */
void cs4224_diags_is_vco_locked(
    cs_uint32 slice,
    cs4224_vco_lock_status_t *vco)
{
    cs_uint16  line_lock_status,  host_lock_status;
    cs_uint16  line_altct_status, host_altct_status;

    vco->rx_line_lock = FALSE;
    vco->rx_host_lock = FALSE;

    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS,  &line_lock_status); 
    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXVCO0_ALTCT_STATUS, &line_altct_status); 

    cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTSTATUS,  &host_lock_status); 
    cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_RXVCO0_ALTCT_STATUS, &host_altct_status); 

    if ((cs4224_is_hw_simplex(slice) && cs4224_line_rx_to_host_tx_dir(slice)) ||
        (cs4224_is_hw_duplex(slice)))
    {
        if (((line_lock_status  & 0x0041) == 0x0041) &&
             (line_altct_status & 0x8000))
        {
            vco->rx_line_lock = TRUE;
            if (cs4224_is_hw_simplex(slice))
            {
                vco->rx_host_lock = TRUE;
            }
        }
    }
    if ((cs4224_is_hw_simplex(slice) && !cs4224_line_rx_to_host_tx_dir(slice)) ||
        (cs4224_is_hw_duplex(slice)))
    {
        if (((host_lock_status  & 0x0041) == 0x0041) &&
             (host_altct_status & 0x8000))
        {
            vco->rx_host_lock = TRUE;
            if (cs4224_is_hw_simplex(slice))
            {
                vco->rx_line_lock = TRUE;
            }
        }
    }
}


/**
 * This is an internal debug method that is used to display
 * the temperature as part of the diagnostics status report
 *
 * @param slice     [I] - The slice of the device to read
 *                        the temperature on.
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_temperature(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint32 temp = 0;
    cs4224_mon_temp_read_fixp(slice, &temp);
    CS_SNPRINTF((buffer, len, "%05d", temp));
    return buffer;
}

/**
 * This is an internal debug method that is used to display
 * the reset count as part of the diagnostics status report
 *
 * @param slice     [I] - The slice of the device to read
 *                        the reset count on.
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_reset_count(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint32 count = 0;
    int offset = 0;
    cs_uint16 data;
    
    if(interface == CS4224_CFG_HOST_SIDE)
    {
        offset = 0x800;
    }
    
    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_RESET_COUNT_MSB + offset, &data);
    count = (cs_uint32)data << 16;
    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_RESET_COUNT_LSB + offset, &data);
    count |= (cs_uint32)data;
    
    CS_SNPRINTF((buffer, len, "%x", count));
    
    return buffer;
}


/**
 * This is an internal method to get the edc mode in human-readable format.
 *
 * This method is somewhat inefficient and should probably be combined with
 * the already existing method cs4224_translate_edc_mode to save code space.
 * Right now the strings returned from the other method are too verbose.
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_edc_mode(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    e_cs4224_mseq_id  mseq_id;
    e_cs4224_edc_mode edc_mode;
    const char* output;

    if(interface == CS4224_CFG_LINE_SIDE) 
    {
        mseq_id = CS4224_DPLX_LINE_MSEQ;
    }
    else
    {
        mseq_id = CS4224_DPLX_HOST_MSEQ;
    }

    cs4224_query_edc_mode(slice, mseq_id, &edc_mode);

    switch(edc_mode)
    {
        case CS_HSIO_EDC_MODE_DISABLED:
        {
            output = "OFF";
            break;
        }
        case CS_HSIO_EDC_MODE_CX1:
        {
            output = "CX1";
            break;
        }
        case CS_HSIO_EDC_MODE_SR:
        {
            output = "SR";
            break;
        }
        case CS_HSIO_EDC_MODE_ZR:
        {
            output = "ZR";
            break;
        }
        case CS_HSIO_EDC_MODE_DWDM:
        {
            output = "DWDM";
            break;
        }
        case CS_HSIO_EDC_MODE_10G_BP:
        {
            output = "10G_BP";
            break;
        }
        case CS_HSIO_EDC_MODE_15G_BP:
        {
            output = "15G_BP";
            break;
        }
        case CS_HSIO_EDC_MODE_5G_BP:
        {
            output = "5G_BP";
            break;
        }
        case CS_HSIO_EDC_MODE_7p5G_BP:
        {
            output = "7p5GBP";
            break;
        }
        case CS_HSIO_EDC_MODE_8p5G_BP:
        {
            output = "8p5GBP";
            break;
        }
        case CS_HSIO_EDC_MODE_FCAN:
        {
            output = "FCAN";
            break;
        }
        case CS_HSIO_EDC_MODE_15G_BP_27dB:
        {
            output = "15G_27";
            break;
        }
        default:
        {
            output = "???";
            break;
        }
    }

    CS_SNPRINTF((buffer, len, "%s", output));
    buffer[len] = 0;

    return buffer;
}


/**
 * This is an internal method used to format the voltage in order to display
 * it in the status report
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_voltage_0p9(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint32 voltage = 0;
    cs4224_mon_volt_read_fixp(slice, CS4224_VLT_SUPPLY_0p9V, &voltage);
    CS_SNPRINTF((buffer, len, "%05d", voltage));
    
    return buffer;
}


/**
 * This is an internal method used to format the voltage in order to display
 * it in the status report
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_voltage_1p8(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint32 voltage = 0;
    cs4224_mon_volt_read_fixp(slice, CS4224_VLT_SUPPLY_1p8V, &voltage);
    CS_SNPRINTF((buffer, len, "%05d", voltage));
    
    return buffer;
}


/**
 * This is an internal method used to format the SKU in order to display
 * it in the status report
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_sku(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint16 sku;
    const char* sku_string = NULL;
    cs4224_reg_get_channel(slice, CS4224_EFUSE_PDF_SKU, &sku);
    
    switch(sku & 0x17)
    {
        /* production */
        case CS4224_HW_CS4223:
        {
            sku_string = "4223-4D"; break;
        }
        case CS4224_HW_CS4224:
        {
            sku_string = "4224-16S"; break;
        }
        case CS4224_HW_CS4343:
        {
            sku_string =  "4343-8D"; break;
        }
        case CS4224_HW_CS4221:
        {
            sku_string = "4221-10S"; break;
        }
        case CS4224_HW_CS4227:
        {
            sku_string = "4227-2D"; break;
        }
        case CS4224_HW_CS4210:
        {
            sku_string = "4210-16S"; break;
        }
        case CS4224_HW_CS4341:
        {
            sku_string = "4341-8D"; break;
        }
        default:
        {
            sku_string = "--"; break;
        }
    }
            
    /* Check to see if this is an engineering SKU */
    if(0x8 == (sku & 0x8))
    {
        CS_SNPRINTF((buffer, len, "%sE", sku_string));
    }
    else
    {
        CS_SNPRINTF((buffer, len, "%sP", sku_string));
    }

    return buffer;
}


/**
 * This is an internal method to display the clock divider configuration.
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_dividers(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint32 clkdiv_ctrl_addr;
    cs_uint16 reg_data;
    const char* fastdiv = NULL;
    const char* ddiv = NULL;
    const char* rdiv = NULL;

    if(interface == CS4224_CFG_LINE_SIDE) 
    {
        clkdiv_ctrl_addr = CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
    }
    else
    {
        clkdiv_ctrl_addr = CS4224_PP_HOST_SDS_COMMON_SRX0_RX_CLKDIV_CTRL;
    }

    cs4224_reg_get_channel(slice, clkdiv_ctrl_addr, &reg_data);

    switch(reg_data & 0xF)
    {
        case 0: rdiv="/8"; break;
        case 1: rdiv="/16"; break;
        case 2: rdiv="/32"; break;
        case 3: rdiv="/40"; break;
        case 4: rdiv="/64"; break;
        case 5: rdiv="/66"; break;
        case 6: rdiv="/80"; break;
        case 7: rdiv="/100"; break;
        case 8: rdiv="/128"; break;
        case 9: rdiv="/FRC"; break;
        default: rdiv="???"; break;
    }

    switch((reg_data >> 4) & 0xF)
    {
        case 0: ddiv="/1"; break;
        case 1: ddiv="/2"; break;
        case 2: ddiv="/4"; break;
        case 3: ddiv="/8"; break;
        case 4: ddiv="/16"; break;
        case 5: ddiv="/32"; break;
        case 6: ddiv="/64"; break;
        case 7: ddiv="/128"; break;
        default: ddiv="???"; break;
    }

    switch((reg_data >> 12) & 0xF)
    {
        case 0: fastdiv="/8"; break;
        case 1: fastdiv="/16"; break;
        case 2: fastdiv="/32"; break;
        case 3: fastdiv="/40"; break;
        case 4: fastdiv="/64"; break;
        case 5: fastdiv="/66"; break;
        case 6: fastdiv="/80"; break;
        case 7: fastdiv="/100"; break;
        case 8: fastdiv="/128"; break;
        case 9: fastdiv="/FRC"; break;
        default: fastdiv="???"; break;
    }

    CS_SNPRINTF((buffer, len, "%4s,%4s,%4s", rdiv, ddiv, fastdiv));

    return buffer;
}


/**
 * This is an internal method to display the fractional divider configuration.
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_fracn(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint16 reg_data;
    cs_uint32 numerator;
    cs_uint8 divisor;
    int offset = 0;

    if(interface == CS4224_CFG_HOST_SIDE) 
    {
        offset = 0x800;
    }

    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RDIVFRAC0_NUMERATOR1 + offset, &reg_data);
    numerator = (cs_uint32)reg_data << 16;
    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RDIVFRAC0_NUMERATOR0 + offset, &reg_data);
    numerator |= (cs_uint32)reg_data;

    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_FRAC0_INTDIV + offset, &reg_data);
    divisor = reg_data & 0xff;

    CS_SNPRINTF((buffer, len, "%6x,%4x", numerator, divisor));

    return buffer;
}


/**
 * This is an internal method to display the polarity inversion configuration
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_polarity_inversion(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint16 reg_data;
    int offset = 0;
    cs_boolean analog_tx;
    cs_boolean digital_tx;
    cs_boolean digital_rx;

    if(interface == CS4224_CFG_HOST_SIDE) 
    {
        offset = 0x800;
    }

    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CONFIG + offset, &reg_data);
    analog_tx = (reg_data >> 11) & 0x1;

    if(interface == CS4224_CFG_LINE_SIDE)
    {
        cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_COMMON_TX0_Config, &reg_data);
    }
    else
    {
        cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_TX0_Config, &reg_data);
    }

    digital_tx = (reg_data >> 2) & 0x1; 
    
    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RX0_Config + offset, &reg_data);
    digital_rx = (reg_data >> 2) & 0x1; 

    CS_SNPRINTF((buffer, len, "%s%s%s",
            analog_tx  == 1 ? "+AlgTX" : " ",
            digital_tx == 1 ? "+DigTx" : " ",
            digital_rx == 1 ? "+DigRX" : " "));

    if(3 == CS_STRLEN(buffer)) /* 3 spaces */
    {
        CS_SNPRINTF((buffer, len, "Off"));
    } 

    return buffer;
}


/**
 * This is an internal method to display the RX lock status
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_rxlock(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint16 reg_data;
    int offset = 0;

    if(interface == CS4224_CFG_HOST_SIDE) 
    {
        offset = 0x800;
    }

    cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS + offset, &reg_data);

    CS_SNPRINTF((buffer, len, "%s", (reg_data & 0x40) == 0x40 ? "Yes" : "No"));

    return buffer;
}


/**
 * This method is called to query the status of each of the line
 * side PCSes and display it.
 *
 * @param slice     [I] - The slice of the device to read
 * @param interface [I] - The interface being accessed (CS_STATUS_INTF_LINE
 *                        or CS_STATUS_INTF_HOST
 * @param buffer    [I] - The buffer to write data to.
 * @param len       [I] - The length of the buffer to write to.
 *
 * @return The formatted buffer
 *
 * @private
 */
const char* cs4224_diags_format_pcs_status(
    cs_uint32 slice,
    int       interface,
    char*     buffer,
    int       len)
{
    cs_uint16 data;
    cs_uint16 pcs_data;
    cs_status status = CS_OK;
    cs_boolean xgpcs_enabled = FALSE;
    cs_boolean xgpcs_synced  = FALSE;
    cs_boolean xgpcs_high_ber = FALSE;
    cs_boolean egpcs_enabled = FALSE;
    cs_boolean egpcs_synced  = FALSE;
    cs_boolean gigepcs_enabled = FALSE;
    cs_boolean gigepcs_synced  = FALSE;

    if(interface == CS4224_CFG_HOST_SIDE)
    {
        return "";
    }

    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_LINEMISC_CLKEN, &data);

    /* If the XGPCS is enabled then query it's status */
    if(CS_BIT2 == (data & CS_BIT2))
    {
        /* Ensure the XGPCS is out of reset */
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_XGPCS_RX_RXCNTRL, &pcs_data);
        if(!(CS_BIT15 == (pcs_data & CS_BIT15)))
        {
            xgpcs_enabled = TRUE;
            xgpcs_synced = TRUE;
            xgpcs_high_ber = FALSE;

            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_XGPCS_RX_RXSTATUS, &pcs_data);

            /* If the 10G PCS is enable but synced then the link is not ready */
            if(!(CS_BIT8 == (pcs_data & CS_BIT8)))
            {
                xgpcs_synced = FALSE;
            }                        

            /* If the 10G PCS is showing bit errors then the link is not ready */
            if(CS_BIT9 == (pcs_data & CS_BIT9))
            {
                xgpcs_high_ber = TRUE;
            }
        }
    } 
    /* Else if the 8G PCS is enabled then check it's PCS sync status */
    else if(CS_BIT1 == (data & CS_BIT1))
    {
        /* Ensure the 8G PCS is out of reset */
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_EGPCS_RX_MODE, &pcs_data);
        if(!(CS_BIT15 == (pcs_data & CS_BIT15)))
        {
            egpcs_enabled = TRUE;
            egpcs_synced = TRUE;

            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_EGPCS_RX_INTSTATUS, &pcs_data);

            /* If the EGPCS is not synced then the link is not ready */
            if(!(CS_BIT0 == (pcs_data & CS_BIT0)))
            {
                egpcs_synced = FALSE;
            }
        }
    }
    /* Else if the 1G PCS is enabled then check it's PCS sync status */
    else if(CS_BIT0 == (data & CS_BIT0))
    {
        /* Ensure the 1G PCS is out of reset */
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_GIGEPCS_LINE_CONTROL, &pcs_data);
        if(!(CS_BIT15 == (pcs_data & CS_BIT15)))
        {
            gigepcs_enabled = TRUE;
            gigepcs_synced = TRUE;

            /* If the 1G PCS is not showing sync then the link isn't ready */
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_GIGEPCS_LINE_STATUS, &pcs_data);
            if(!(CS_BIT2 == (pcs_data & CS_BIT2)))
            {
                gigepcs_synced = FALSE;
            }
        }
    }
    
    CS_SNPRINTF((buffer, len, "%6s|%6s|%6s",
                xgpcs_enabled ? (xgpcs_synced ? (xgpcs_high_ber ? "Y+BER" : "Y") : "N") : "-",
                egpcs_enabled ? (egpcs_synced ? "Y" : "N") : "-",
                gigepcs_enabled ? (gigepcs_synced ? "Y" : "N") : "-"));

    return buffer;
}


/**
 * This structure is used by the diagnostics status in order to
 * know how to format a field in the summary report.
 *
 * @private
 */
typedef struct cs_edc_field_s
{
    /** the register address (if applicable) */
    cs_uint32   reg_addr;

    /** A label to associate with a field in the report */
    const char* field_label;

    /**
     * The format of the field, currently only 'x' or 's'
     * are supported
     */
    const char* field_format;

    /** The width of the field */
    int         field_width;

    /** An optional callback used to format the field */
    const char* (*callback)(cs_uint32 slice, int interface, char* buffer, int len);
}cs_edc_field_t;


/**
 * This structure is used to define an entry in
 * each section of the status summary
 *
 * @private
 */
typedef struct cs_edc_row_s
{
    /** This is a label to associate with a row of the report */
    const char* label;

    /** The number of instances of the section */
    int instances;

    /** The number of columns in this section */
    int cols;

    /**
     * This is an include mask that is used to define whether or
     * not the row should be displayed
     */
    cs_uint16   include_mask;

    /**
     * This is the list of fields in that row or section of
     * the report. This must be changed if more fields
     * are displayed
     */
    cs_edc_field_t fields[14];
}cs_edc_row_t;


/**
 * This array defines the rows that are part of the status report
 *
 * @private
 */
cs_edc_row_t g_edc_fields[] = 
{
    /* Global status */
    {
        "Global Status",
        1,  /* Only one global instance, no port pair registers */
        14, /* The number of columns in the array below */
        CS4224_STATUS_GLOBAL,
        {
            {0,                                              "SKU",      "s", 10, cs4224_diags_format_sku},
            {CS4224_EFUSE_PDF_MON_CAL_DATA,                  "EFCAL",    "x", 5, NULL},
            {CS4224_EFUSE_PDF_MON_GAIN_DATA,                 "EFGAI",    "x", 5, NULL},
            {CS4224_GLOBAL_UCODE_TIMESTAMP0,                 "TIME0",    "x", 5, NULL},
            {CS4224_GLOBAL_UCODE_TIMESTAMP1,                 "TIME1",    "x", 5, NULL},
            {CS4224_GLOBAL_UCODE_TIMESTAMP2,                 "TIME2",    "x", 5, NULL},
            {CS4224_GLOBAL_DWNLD_CHECKSUM_HW,                "CHKHW",    "x", 5, NULL},
            {CS4224_GLOBAL_DWNLD_CHECKSUM_SW,                "CHKSW",    "x", 5, NULL},
            {CS4224_GLOBAL_PIN_STATUS,                       "PINST",    "x", 5, NULL},
            {CS4224_EEPROM_LOADER_STATUS,                    "EPSTS",    "x", 5, NULL},
            {CS4224_GLOBAL_SCRATCH7,                         "APIVER",   "x", 6, NULL},
            {0,                                              "Temp",     "s", 5, cs4224_diags_format_temperature},
            {0,                                              "1.8V",     "s", 5, cs4224_diags_format_voltage_1p8},
            {0,                                              "0.9V",     "s", 5, cs4224_diags_format_voltage_0p9},
        }
    },
    /* SERDES status like locks and transmit coefficients */
    {
        "Serdes Status",
        2,  /* 2 instances = Line + host */
        9, /* The number of columns in the array below */
        CS4224_STATUS_SERDES,
        {
            {0,                                              "Lock",    "s", 4, cs4224_diags_format_rxlock}, 
            {CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT,   "LockI",   "x", 5, NULL},
            {CS4224_PP_LINE_SDS_COMMON_RXVCO0_STATUS,        "Freq",    "x", 4, NULL}, 
            {0,                                              "EDC MD",  "s", 6, cs4224_diags_format_edc_mode}, 
            {CS4224_PP_LINE_SDS_COMMON_STX0_TX_OUTPUT_CTRLA, "CTLA",    "x", 4, NULL},
            {CS4224_PP_LINE_SDS_COMMON_STX0_TX_OUTPUT_CTRLB, "CTLB",    "x", 4, NULL},
            {CS4224_PP_LINE_SDS_COMMON_STX0_SQUELCH,         "Sqlch",   "x", 5, NULL},
            {CS4224_PP_LINE_SDS_COMMON_SRX0_RX_CPA,          "RX_CPA",  "x", 6, NULL},
            {CS4224_PP_LINE_SDS_COMMON_RXVCO0_STATUS,        "VCOSTAT", "x", 7, NULL},
            
        }
    },

    /* Clocking Dividers and Lane Mappings */
    {
        "Receive Clocking/Polarity Inversion",
        2, /* 2 instances = Line + host */
        3, /* The number of columns in the array below */
        CS4224_STATUS_CLOCKING,
        {
            {0,                               "RDIV,DDIV,FDIV",     "s", 14, cs4224_diags_format_dividers},
            {0,                               "Numrtr,Div ",        "s", 11, cs4224_diags_format_fracn},
            {0,                               "Polarity Inversion", "s", 18, cs4224_diags_format_polarity_inversion},
        }
    },

    /* Microsequencer status */
    {
        "Microsequencer Status",
        2,  /* 2 instances = Line + host */
        10,  /* The number of columns in the array below */
        CS4224_STATUS_MSEQ,
        {
            {CS4224_PP_LINE_SDS_DSP_MSEQ_STATUS,           "MSQ_STA",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_ENABLE,           "MSQ_ENB",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_OPTIONS_SHADOW,   "OPTIONS",  "x", 7, NULL},
            {0,                                            "RSTCNT",   "s", 8, cs4224_diags_format_reset_count},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_EQADJ1,    "EQAD1",    "x", 5, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_EQADJ2,    "EQAD2",    "x", 5, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL,     "PHSEL",    "x", 6, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_AGC_GAIN,  "AGC_GN",   "x", 6, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_MSB,   "PWRDN_M",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_POWER_DOWN_LSB,   "PWRDN_L",  "x", 7, NULL},
        }
    },

    /* Microsequencer spare registers */
    {
        "Microsequencer Spares",
        2,  /* 2 instances = Line + host */
        9,  /* The number of columns in the array below */
        CS4224_STATUS_MSEQ,
        {
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE1_LSB,       "SP1_LSB",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE1_MSB,       "SP1_MSB",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE3_LSB,       "SP3_LSB",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE3_MSB,       "SP3_MSB",  "x", 7, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE10_LSB,      "SP10_LSB", "x", 8, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE10_MSB,      "SP10_MSB", "x", 8, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB,      "SP12_LSB", "x", 8, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE16_LSB,      "SP16_LSB", "x", 8, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE19_LSB,      "SP19_LSB", "x", 8, NULL},
        }
    },
    
    /* Line Interrupt status, two of them since there are a lot of line registers */
    {
        "Line Interrupts",
        1,  /* 2 instances = Line + host */
        9,  /* The number of columns in the array below */
        CS4224_STATUS_LINE_INTERRUPT,
        {
            {0x1051,                                           "RXVCO0",       "x", 6,  NULL},
            {CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT,     "RXLOCKD0",     "x", 8,  NULL}, 
            {CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_INTERRUPT,     "PRBSCHK0",     "x", 8,  NULL}, 
            {CS4224_PP_LINE_SDS_DSP_COEF_SATURATED_INT,        "DSP_SAT",      "x", 7,  NULL}, 
            {0x1439,                                           "EMDS",         "x", 4,  NULL},
            {CS4224_PP_LINE_GIGEPCS_INT_LINE_PCS1GE_INTERRUPT, "PCS1GE",       "x", 6,  NULL},
            {CS4224_PP_LINE_EGPCS_RX_INTERRUPT,                "EGPCS_RX",     "x", 8,  NULL},
            {CS4224_PP_LINE_EGPCS_TX_INTERRUPT,                "EGPCS_TX",     "x", 8,  NULL},
            {CS4224_PP_LINE_XGPCS_RX_RXINT,                    "XGPCS_RX",     "x", 8,  NULL},
        }
    },
    {
        "Line Protocol Interrupts",
        1,  /* 2 instances = Line + host */
        9,  /* The number of columns in the array below */
        CS4224_STATUS_LINE_INTERRUPT,
        {
            {CS4224_PP_LINE_AN_TX_AN_COMPLETE_STATUS_INT,      "AN_COMP",      "x", 7,  NULL},
            {CS4224_PP_LINE_AN_TX_MAIN_INT,                    "AN_TX_MAIN",   "x", 10, NULL},
            {CS4224_PP_LINE_AN_TX_TX_AFIFO_INT,                "AN_TX_AFIFO",  "x", 11, NULL},
            {CS4224_PP_LINE_AN_RX_MAIN_INT,                    "AN_RX_MAIN",   "x", 10, NULL},
            {CS4224_PP_LINE_AN_RX_RX_AFIFO_INT,                "AN_RX_AFIFO",  "x", 11, NULL},
            {CS4224_PP_LINE_TP_TX_TRAINING_INT,                "TP_TX_TRAIN",  "x", 11, NULL},
            {CS4224_PP_LINE_TP_RX_FRAME_LOCK_INT,              "TP_RX_FL",     "x", 8,  NULL},
            {CS4224_PP_LINE_KR_FEC_TX_INT,                     "KR_FEC_TX",    "x", 9,  NULL},
            {CS4224_PP_LINE_KR_FEC_RX_INT,                     "KR_FEC_RX",    "x", 9,  NULL},
        }
    },
    
    /* Host Interrupt Status */
    {
        "Host Interrupts",
        1,  /* 2 instances = Line + host */
        6,  /* The number of columns in the array below */
        CS4224_STATUS_HOST_INTERRUPT,
        {
            {0x1851,                                           "RXVCO0",   "x", 6, NULL},
            {CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTERRUPT,     "RXLOCKD0", "x", 8, NULL},
            {CS4224_PP_HOST_SDS_COMMON_PRBSCHK0_INTERRUPT,     "PRBSCHK0", "x", 8, NULL},
            {CS4224_PP_HOST_SDS_DSP_COEF_SATURATED_INT,        "DSP_SAT",  "x", 7, NULL},
            {0x1c39,                                           "EMDS",     "x", 4, NULL},
            {CS4224_PP_HOST_GIGEPCS_INT_HOST_PCS1GE_INTERRUPT, "PCS1GE",   "x", 6, NULL},
        }
    },

    /* Link Status */
    {
        "Link Status",
        1,  /* One instance showing line + host */
        5,
        CS4224_STATUS_LINK,
        {
            {CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTSTATUS, "Line", "x", 4, NULL},
            {CS4224_PP_LINE_SDS_DSP_MSEQ_STATUS,           "MSEQ", "x", 4, NULL},
            {0,                                            "10GPCS| 8GPCS| 1GPCS",  "s", 21, cs4224_diags_format_pcs_status},

            {CS4224_PP_HOST_SDS_COMMON_RXLOCKD0_INTSTATUS, "Host", "x", 4, NULL},
            {CS4224_PP_HOST_SDS_DSP_MSEQ_STATUS,           "MSEQ", "x", 4, NULL},
        }
    }
};


/**
 * This method is called to show the overall status of the device
 * for a particular set of slices. This method will not work properly
 * on simplex devices right now. This will be added in the future.
 *
 * This method is only defined if CS_DONT_USE_STDLIB is not defined
 * implying that the C standard library is available. It uses sprintf()
 * and the CS_PRINTF() macro to display output which may not be
 * possible on systems that do not have a console.
 *
 * The following tables describe the format of each of these
 * sections:
 *
 * @{table,
 * -t Global Status (STATUS_GLOBAL)
 * -h Column | Description
 * - Sl      | The slice/channel number
 * - SKU     | The SKU identifying the device
 * - EFCAL   | Calibration constants programmed on the device
 * - EFGAI   | Calibration constants programmed on the device
 * - TIME0   | The microcode timestamp (MM/DD)
 * - TIME1   | The microcode timestamp (YYYY)
 * - TIME2   | The microcode timestamp (HH/MM)
 * - CHKHW   | The calculated hardware checksum
 * - CHKSW   | The calculated software checksum
 * - PIN_ST  | The value of the pin status register
 * - EP_STS  | The value of the EEPROM status register
 * - API_VER | The verion of the API used to program the ASIC.
 * }
 *
 * @{table,
 * -t SERDES Status (STATUS_SERDES)
 * -h Column  | Description
 * - Sl       | The slice/channel number
 * - Lock     | Whether or not the lock detector is locked
 * - LockI    | The current value of the lock detect interrupt register
 * - Freq     | The VCO frequency slot
 * - EDC MD   | The configured EDC mode such as CX1, SR, etc.
 * - CTRLA    | The main cursor
 * - CTRLB    | The pre and post cursors
 * - Squelch  | 1 if the TX is squelched, 0 if not
 * - Temp     | The measured temperature from the die
 * - 1.8V     | The measured voltage of the die
 * - 0.9V     | The measured voltage of the die
 * }
 *
 * @{table,
 * -t Receive Clocking (STATUS_CLOCKING)
 * -h Column            | Description
 * - Sl                 | The slice/channel number
 * - RDIV,DDIV,FDIV     | The configuration of the three clock dividers RDIV, DDIV and FASTDIV.
 * - Nmrtr,Div          | The configuration of the fractional divider (Numerator, Divisor)
 * - Polarity Inversion | The configuration of any polarity inversions (Blank if none are enabled)
 * }
 *
 * @{table,
 * -t Microsequencer Status (STATUS_MSEQ)
 * -h Column | Description
 * - Sl      | The slice/channel number
 * - MSEQ_STA | The current value of the MSEQ_STATUS register showing info like EDC convergence
 * - RSTCNT   | Microsequencer reset count (increments if RX lock is lost)
 * - EQADJ1   | Microsequencer calibration information
 * - EQADJ2   | Microsequencer calibration information
 * - PHSEL    | Microsequencer calibration information
 * - AGC_GN   | Microsequencer calibration information
 * - PWRDN_M  | Microsequencer status information
 * - PWRDN_L  | Microsequencer status information
 * }
 *
 * @param slice_start         [I] - The slice to start the dump from
 * @param slice_end           [I] - The slice to end the dump at.
 * @param sections_to_display [I] - A mask defining the sections of the report
 *                                  to display, use e_cs4224_status_mask
 *
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @example
 *
 *     // Print the full status for slices 0-7
 *     cs4224_diags_show_status(0, 7, CS4224_STATUS_ALL);
 *
 *     // Only print the global and serdes information for slices 0-3
 *     cs4224_diags_show_status(0, 3, CS4224_STATUS_GLOBAL | CS4224_STATUS_SERDES);
 */
cs_status cs4224_diags_show_status(
    cs_uint32 slice_start,
    cs_uint32 slice_end,
    cs_uint16 sections_to_display)
{
    cs_uint32 i,j,k,slice;
    cs_uint32 row;
    cs_status status = CS_OK;
    int instance;
    cs_boolean is_simplex = FALSE;

    if(cs4224_is_hw_simplex(slice_start))
    {
        is_simplex = TRUE;
    }

    /* slice printed below will have the EDC address removed, so print it at least once */
    CS_PRINTF(( "\nStatus of EDC %08x\n\n", (cs_uint32)(slice_start & 0xFFFFFF00) ));

    for(instance = 0; instance < 2; instance++)
    {
        for(row = 0; row < sizeof(g_edc_fields)/sizeof(cs_edc_row_t); row++)
        {
            /* If this section is not selected then skip it */
            if((sections_to_display & g_edc_fields[row].include_mask) != g_edc_fields[row].include_mask)
            {
                continue;
            }

            if(g_edc_fields[row].instances == 1 && instance > 0)
            {
                continue;
            } 
            
            if(is_simplex && instance > 0)
            {
                continue;
            }
        
            if(is_simplex || g_edc_fields[row].instances == 1)
            {
                CS_PRINTF(("%s\n", g_edc_fields[row].label));
            }
            else
            {
                if(instance == 0)
                {
                    CS_PRINTF(("Line %s\n", g_edc_fields[row].label));
                }
                else
                {
                    CS_PRINTF(("Host %s\n", g_edc_fields[row].label));
                }
            }
        
            /* Print the top of the header */
            CS_PRINTF(("---+"));
            for(i = 0; i < g_edc_fields[row].cols; i++)
            {
                cs_uint16 field_width = g_edc_fields[row].fields[i].field_width;

                /* Only display the field header if the width > 0 */
                for(k = 0; k < field_width; k++)
                {
                    CS_PRINTF(("-"));
                }

                if(field_width > 0)
                {
                    CS_PRINTF(("+"));
                }
            }
            CS_PRINTF(("\n"));
        
            /* Print the row header */
            CS_PRINTF(("Sl#|"));
            for(i = 0; i < g_edc_fields[row].cols; i++)
            {
                cs_uint16 field_width = g_edc_fields[row].fields[i].field_width;
                const char* field_label = g_edc_fields[row].fields[i].field_label;

                /* Only display the field header if the width > 0 */
                if(field_width > 0)
                {
                    CS_PRINTF(("%*s|", field_width, field_label));
                }
            }
            CS_PRINTF(("\n"));
        
            /* Print the bottom of the row header */
            CS_PRINTF(("---+"));
            for(i = 0; i < g_edc_fields[row].cols; i++)
            {
                cs_uint16 field_width = g_edc_fields[row].fields[i].field_width;

                /* Only display the field header if the width > 0 */
                for(k = 0; k < field_width; k++)
                {
                    CS_PRINTF(("-"));
                }

                if(field_width > 0)
                {
                    CS_PRINTF(("+"));
                }
            }
            CS_PRINTF(("\n"));
            
            
            /* Print the status for each slice of the device for this section
             * of the report. */
            for(slice = slice_start; slice <= slice_end; slice++)
            {
                CS_PRINTF(( "%3d|", (slice&0xFF) ));
                for(j = 0; j < g_edc_fields[row].cols; j++)
                {
                    cs_uint16 field_width = g_edc_fields[row].fields[j].field_width;
                    int interface;
                    
                    /* For simplex SKUs we need to override the interface based on whether
                     * or not it is line vs. host */
                    if(cs4224_is_hw_simplex(slice))
                    {
                        if(cs4224_line_rx_to_host_tx_dir(slice))
                        {
                            interface = CS4224_CFG_LINE_SIDE; 
                        }
                        else
                        {
                            interface = CS4224_CFG_HOST_SIDE; 
                        }
                    }
                    else
                    {
                        if(instance == 0)
                        {
                            interface = CS4224_CFG_LINE_SIDE;
                        }
                        else
                        {
                            interface = CS4224_CFG_HOST_SIDE;
                        }
                    }

                    /* Only display the field if the width > 0 */
                    if(field_width > 0)
                    { 
                        /* If the field has a display callback then call it instead of
                         * grabbing the register data. */
                        if(g_edc_fields[row].fields[j].callback != NULL)
                        {
                            char format_buffer[32];
                            int len = g_edc_fields[row].fields[j].field_width;
                            CS_PRINTF(("%*s|", field_width, g_edc_fields[row].fields[j].callback(slice, interface, format_buffer, len)));
                        }
                        else
                        {
                            cs_uint16 reg_data;
                            cs_uint32 addr = g_edc_fields[row].fields[j].reg_addr;

                            if(instance == 1)
                            {
                                addr += 0x800;
                            }
                            
                            if(addr != 0)
                            {
                                status |= cs4224_reg_get_channel(slice, addr, &reg_data);
                                CS_PRINTF(("%*x|", field_width, reg_data));
                            }
                            else
                            {
                                status |= cs4224_reg_get_channel(slice, addr, &reg_data);
                                CS_PRINTF(("%*s|", field_width, "--"));
                            }
                        }
                    }
                }
                CS_PRINTF(("\n"));
            }
            
            
            /* Print the footer of the row */
            CS_PRINTF(("---+"));
            for(i = 0; i < g_edc_fields[row].cols; i++)
            {
                cs_uint16 field_width = g_edc_fields[row].fields[i].field_width;

                /* Only display the field header if the width > 0 */
                for(k = 0; k < field_width; k++)
                {
                    CS_PRINTF(("-"));
                }

                if(field_width > 0)
                {
                    CS_PRINTF(("+"));
                }
            }
            CS_PRINTF(("\n\n"));
        }
    }

    return status;
}


/** This method dumps out current interrupt stats on all slices of a device,
 *   then resets the state of those interrupts so testing can continue. Similar
 *   to a PRBS check but for non-PRBS status information
 * 
 * @param die  [I] - Uses the upper bits to determine which device to get stats from
 *
 * @return CS_OK on a pass, CS_ERROR otherwise
 * 
 */
cs_status cs4224_diags_show_and_clear_stats(
    cs_uint32 die)
{
    cs_status status = CS_OK;
    cs_uint32 i = 0;
    cs4224_fec_stats_t fec_stats;
    cs_uint16 sections = CS4224_STATUS_GLOBAL | CS4224_STATUS_SERDES | CS4224_STATUS_HOST_INTERRUPT | \
                         CS4224_STATUS_LINE_INTERRUPT | CS4224_STATUS_MSEQ;
    cs_uint32 upper_bits = (die & 0xFFFFFF00);
    cs_uint32 min = upper_bits; /* slice 0 */
    cs_uint32 max = upper_bits | (CS4224_MAX_NUM_SLICES(die)-1); /* slice 7 or 15 */

    CS_PRINTF(("\nCS4224: Stats for die 0x%08x\n\n",upper_bits));

    /* Dump out interrupt information */
    status |= cs4224_diags_show_status(min, max, sections);

    if(!cs4224_is_hw_simplex(die))
    {
        /* FEC is only valid in duplex + KR-AN */
        /* Dump out FEC information */
        CS_PRINTF(("FEC Stats:\n"));
        CS_PRINTF(("sl# | tx_blk_total | rx_blk_total | rx_blk_corr | rx_blk_uncorr | rx_zero_errs | rx_one_errs\n"));
        for(i = 0; i < CS4224_MAX_NUM_SLICES(die); i++)
        {
            status |= cs4224_get_fec_stats( (upper_bits | i), &fec_stats );
            CS_PRINTF(( "%3d | %12x | %12x | %11x | %13x | %12x | %11x",
                        i,
                        fec_stats.tx_blk_total,
                        fec_stats.rx_blk_total,
                        fec_stats.rx_blk_corr,
                        fec_stats.rx_blk_uncorr,
                        fec_stats.rx_zero_errs,
                        fec_stats.rx_one_errs
                        ));
            /*check for any errors in the FEC stats */
            if( (0 != fec_stats.rx_blk_corr) || (0 != fec_stats.rx_blk_uncorr) )
            {
                CS_PRINTF(("  ***  ERRORS"));
            }
            CS_PRINTF(("\n"));
        }
    }

    /* Clear all the interrupts */
    for(i = 0; i < CS4224_MAX_NUM_SLICES(die); i++)
    {
        status |= cs4224_diags_clear_interrupts( upper_bits | i );
    }
    
    return status;
}


#endif /* CS_HAS_DEBUG_STATUS_DUMPS == 1 */


#if (CS_HAS_DEBUG_REGISTER_DUMPS == 1)

/**
 * Some registers cannot be read or else you risk breaking the operation of the
 * mseq. This function will return TRUE if you can read from the register address
 * or FALSE if reading will cause errors.
 * 
 * @param addr     [I] - Register address you wish to read from
 * 
 * @return TRUE if register can be read, FALSE otherwise
 * 
 * @private
 */
cs_boolean cs4224_diags_register_can_read(
        cs_uint16 addr)
{
    /* don't read from select register ranges */
    if( (addr >= CS4224_PP_LINE_SDS_DSP_MSEQ_IX && addr <= CS4224_PP_LINE_SDS_DSP_MSEQ_BASE3_INST) ||
        (addr >= CS4224_PP_HOST_SDS_DSP_MSEQ_IX && addr <= CS4224_PP_HOST_SDS_DSP_MSEQ_BASE3_INST) )
    {
        return FALSE;
    }
    return TRUE;
    
}

/**
 * This method is called to dump a range of registers on the device.
 *
 * @param die        [I] - The die of the device to dump registers on
 * @param start_addr [I] - The start address of the range to dump
 * @param end_addr   [I] - The end address of the range to dump. This
 *                         address is included in the register dump.
 * @param registers  [O] - The array to store register values. This must
 *                         be at least as big as (end_addr - start_addr + 1)
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 * @example
 *    cs_uint16 registers[8];
 *    cs_uint32 die = 0;
 *    int i;
 *
 *    // Read the 8 scratch registers (addresses 0x1d - 0x24)
 *    cs4224_diags_register_dump_range(die, 0x1d, 0x1d + 8, registers); 
 *
 *    for(i = 0; i < 8; i++)
 *    {
 *        CS_PRINTF(("%d: %x = %x\\n", i, 0x1d + i, registers[i]));
 *    }
 */
cs_status cs4224_diags_register_dump_range(
        cs_uint32 die,
        cs_uint32 start_addr,
        cs_uint32 end_addr,
        cs_uint16 registers[])
{
    cs_status status = CS_OK;
    cs_uint32 addr;
    
    status |= cs4224_lock(die);

    /* Ensure a valid address was entered */
    if((start_addr > end_addr) || (end_addr > 0x5011))
    {
        return CS_ERROR;
    }

    for(addr = start_addr; addr <= end_addr; addr++)
    {
        if(cs4224_diags_register_can_read(addr))
        {
            status |= cs4224_reg_get(die, addr, &(registers[addr-start_addr]));
        }
        else
        {
            registers[addr-start_addr] = 0xbeef;
        }
    }
    
    status |= cs4224_unlock(die);

    return status;
}

/* $if : CORTINA: Only for regression */
#ifndef CS_DONT_USE_STDLIB
#include <stdlib.h>
/**
 * This is a diagnostics method in Python used to verify the behavior
 * of dumping a range of register addresses.
 *
 * @param die        [I] - The die on which to dump the registers.
 * @param start_addr [I] - The start address to dump
 * @param end_addr   [I] - The end address to dump.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 */
cs_status cs4224_diags_register_dump_range_wrapper(
    cs_uint32 die,
    cs_uint32 start_addr,
    cs_uint32 end_addr)
{
    cs_status status = CS_OK;
    cs_uint16* registers = 0;
    int num = (end_addr - start_addr + 1) * 2;

    /* Allocate space for the register dump */
    registers = (cs_uint16*)malloc(num);
    if(0 == registers)
    {
        CS_TRACE(("ERROR: cannot allocate memory\n"));
        return CS_ERROR;
    }

    for(num = 0; num < (end_addr - start_addr)+1; num++)
    {
        registers[num] = 0xdead;
    }

    /* Dump the range of registers */
    status |= cs4224_diags_register_dump_range(die, start_addr, end_addr, registers);

    for(num = 0; num < (end_addr - start_addr)+1; num++)
    {
        CS_PRINTF(("%04d: %04x = 0x%04x\n", num, start_addr + num, registers[num])); 
    } 

    /* Now free up the allocated space again */
    free(registers);

    return status;
}
#endif
/* $endif : CORTINA */

/**
 * This is an internal array that is used to determine
 * the valid sections of the address map to read when
 * dumping registers. This array consists of:
 *
 *    start_addr, end_addr
 *
 * for each block of registers in the address map.
 */
cs_uint32 g_register_ranges[][2] = 
{
    {0x0,    0xfe},   /* GLOBAL         */
    {0x100,  0x14d},  /* GPIO           */
    {0x180,  0x1d6},  /* EFUSE          */
    {0x200,  0x2a6},  /* MONITOR        */
    {0x2e0,  0x2e9},  /* CLKMON_GBL     */
    {0x300,  0x30e},  /* MSEQ_PS[0]     */
    {0x400,  0x40e},  /* MSEQ_PS[1]     */

    {0x1000, 0x1012}, /* PP[0].LINEMISC */
    {0x1020, 0x10CA}, /* PP[0].LINE_SDS_COMMON */
    {0x1220, 0x12B9}, /* PP[0].LINE_SDS_DSP_MSEQ */
    {0x1320, 0x135D}, /* PP[0].LINE_SDS_DSP */
    {0x1420, 0x1442}, /* PP[0].LINE_EMDS */
    {0x1460, 0x1483}, /* PP[0].LINE_GIGEPCS */
    {0x14a0, 0x14b9}, /* PP[0].LINE_EGPCS */
    {0x14C0, 0x14EF}, /* PP[0].LINE_XGPCS */
    {0x1500, 0x1565}, /* PP[0].LINE_KR_AN */
    {0x1580, 0x15CC}, /* PP[0].LINE_KR_TP */
    {0x1600, 0x1664}, /* PP[0].LINE_KR_FEC */
    {0x1680, 0x168C}, /* PP[0].LINE_MCAN */
    {0x1800, 0x1812}, /* PP[0].HOSTMISC */
    {0x1820, 0x18CA}, /* PP[0].HOST_SDS_COMMON */
    {0x1A20, 0x1AB9}, /* PP[0].HOST_SDS_DSP_MSEQ */
    {0x1B20, 0x1B5D}, /* PP[0].HOST_SDS_DSP */
    {0x1C20, 0x1C42}, /* PP[0].HOST_EMDS */
    {0x1C60, 0x1C83}, /* PP[0].HOST_GIGEPCS */

    {0x5000, 0x5011}, /* EEPROM     */
};


/**
 * This method is called to dump the entire register map for a
 * single die of the device.
 *
 * @param die [I] - The die of the device to dump registers for 
 *
 */
void cs4224_diags_register_dump_die(cs_uint32 die)
{
    cs_uint32 range;
    CS_PRINTF(("DIE %d\n-----------\n", die));
    
    cs4224_lock(die);

    for(range = 0; range < (sizeof(g_register_ranges)/sizeof(g_register_ranges[0])); range++)
    {
        cs_uint32 start = g_register_ranges[range][0];
        cs_uint32 end   = g_register_ranges[range][1];
        cs_uint32 addr;
        cs_uint16 reg_data = 0;

        /* Expand the port-pair registers to handle all instances */
        if(start >= 0x1000 && start < 0x5000)
        {
            int instance = 0;

            for(instance = 0; instance < 4; instance++)
            {
                for(addr = start; addr < end+1; addr++)
                {
                    if(cs4224_diags_register_can_read(addr))
                    {
                        cs4224_reg_get(die, addr + (instance * 0x1000), &reg_data);
                    }
                    else
                    {
                        reg_data = 0xbeef;
                    }
                    CS_PRINTF(("0x%04x = 0x%04x\n", addr + (instance * 0x1000), reg_data));
                }
            }
        }
        else
        {
            for(addr = start; addr < end+1; addr++)
            {
                if(cs4224_diags_register_can_read(addr))
                {
                    cs4224_reg_get(die, addr, &reg_data);
                }
                else
                {
                    reg_data = 0xbeef;
                }
                CS_PRINTF(("0x%04x = 0x%04x\n", addr, reg_data));
            }
        }
    }
    
    cs4224_unlock(die);
}


e_cs4224_hardware_id cs4224_hw_id(cs_uint32 slice);

/**
 * This method is called to dump the entire register map for all
 * dies in the device.
 *
 * @deprecated
 *   This method has been deprecated, use cs4224_diags_register_dump_asic 
 *   instead.
 */
void cs4224_diags_register_dump(void)
{
    int max_dies = 2;
    int die;

    if(CS4224_HW_CS4223 == cs4224_hw_id(0))
    {
        max_dies = 1;
    }

    for(die = 0; die < max_dies; die++)
    {
        cs4224_diags_register_dump_die(die);
    }
}

/**
 * This method is called to dump the entire register map for all
 * dies in the selected device.
 *
 * @param slice [I] - The slice parameter is only used to select
 *                    the ASIC to dump the registers for. It can
 *                    be any slice on that particular device.
 */
void cs4224_diags_register_dump_asic(
    cs_uint32 slice)
{
    cs_uint8  max_dies = CS4224_MAX_NUM_DIES(slice);
    cs_uint8  die;
    cs_uint32 asic_die;

    for(die = 0; die < max_dies; die++)
    {
        asic_die = (slice & 0xffffff00) | die;

        cs4224_diags_register_dump_die(asic_die);
    }
}

#endif /* CS_HAS_DEBUG_REGISTER_DUMPS == 1 */


/* $if : CORTINA : Only for regression usage right now */

/** @private */
void cs4224_diags_debug_loopback_test(cs_uint32 slice)
{
    cs_status status = CS_OK;

    CS_PRINTF(("enabling loopbacks\n"));
    status |= cs4224_diags_loopback_enable(slice, CS4224_LOOPBK_DUPLEX_FAR_DATA, CS4224_LOOPBK_HOST);

    CS_MDELAY(4000);

    CS_PRINTF(("enabling loopbacks again\n"));
    status |= cs4224_diags_loopback_enable(slice, CS4224_LOOPBK_DUPLEX_FAR_DATA, CS4224_LOOPBK_HOST);

    CS_MDELAY(4000);

    CS_PRINTF(("disabling loopbacks\n"));
    status |= cs4224_diags_loopback_disable(slice, CS4224_LOOPBK_DUPLEX_FAR_DATA, CS4224_LOOPBK_HOST);

    CS_MDELAY(4000);

    CS_PRINTF(("disabling loopbacks again\n"));
    status |= cs4224_diags_loopback_disable(slice, CS4224_LOOPBK_DUPLEX_FAR_DATA, CS4224_LOOPBK_HOST);


}

/* $endif : CORTINA */



/* $if : CORTINA : Internal stuff only */

/* Calibration status registers for the microsequencer */
#define CS4224_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL  0x1265
#define CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL1 0x1250
#define CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL2 0x1251
#define CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL3 0x126d
#define CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL4 0x125e
#define CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL5 0x125f


/**
 * This is a diagnostic method that is used to sweep the calibration parameters
 * of the device for performance analysis.
 *
 * @param slice_start    [I] - The start of the slice to sweep
 * @param slice_end      [I] - The end slice to sweep
 * @param sweep_duration [I] - The duration of each sample
 *
 * @return CS_OK on success, CS_ERROR on failure
 * 
 * @private
 */
cs_status cs4224_diags_sweep_calibration_parameters(
    cs_uint32 slice_start,
    cs_uint32 slice_end,
    cs_uint32 sweep_duration)
{
    cs_uint32 slice;
    cs_uint16 phsel;
    cs_status status = CS_OK;
    cs_uint16 reg_data;
    
    CS_PRINTF(("---+-----+-----+-----+----+--------+-----+----+----+\n"));
/* $if : CORTINA : Don't show the real header externally */
    CS_PRINTF(("Sl#|PHSEL|DFE0N|DFE0P|SNR0|PRBS    |LOCK |EQ1 |EQ2 |\n"));
/* $endif : CORTINA */
    CS_PRINTF(("Sl#|PH   |CAL1 |CAL2 |CAL3|PRBS    |LOCK |CAL4|CAL5|\n"));
    CS_PRINTF(("---+-----+-----+-----+----+--------+-----+---------+\n"));
        
    /* If power savings is enabled then need to disable it */
    for(slice = slice_start; slice <= slice_end; slice++)
    {
        cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB, 0x80);
        cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE0_LSB, 0);
        cs4224_reg_set_channel(slice, CS4224_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL, 0x20);
    }

    CS_MDELAY(10);

    for(slice = slice_start; slice <= slice_end; slice++)
    {
        /* Sweep high from the assumed center point and capture the calibration status. */
        for(phsel = 0x20; phsel <= 0x34; phsel++)
        {
            cs_uint32 prbscnt;
            cs_uint16 lockd0;
            cs_uint16 cal1;
            cs_uint16 cal2;
            cs_uint16 cal3;
            cs_uint16 cal4;
            cs_uint16 cal5;

            CS_PRINTF(("%3d|%5d", slice, phsel));

            /* Clear the lock detect interrupt */
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT, 0xffff);

            /* Select the phase point */
            status |= cs4224_reg_set_channel(slice, CS4224_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL, phsel);

            CS_MDELAY(sweep_duration);
            
            /* Read back the calibration status registers */
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT, &lockd0);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL1, &cal1);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL2, &cal2);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL3, &cal3);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL4, &cal4);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL5, &cal5);

            /* Read back PRBS count */
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count1, &reg_data);
            prbscnt = (cs_uint32)reg_data << 16;
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count0, &reg_data);
            prbscnt |= (cs_uint32)reg_data;
            
            CS_PRINTF(("|%5x|%5x|%4x|%8x|%5x|%4x|%4x|\n", cal1, cal2, cal3, prbscnt, lockd0, cal4, cal5));
        }
        
        /* Sweep low from the assumed center point and capture the calibration status. */
        for(phsel = 0x20; phsel >= 0x10; phsel--)
        {
            cs_uint32 prbscnt;
            cs_uint16 lockd0;
            cs_uint16 cal1;
            cs_uint16 cal2;
            cs_uint16 cal3;
            cs_uint16 cal4;
            cs_uint16 cal5;

            CS_PRINTF(("%3d|%5d", slice, phsel));

            /* Clear the lock detect interrupt */
            status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT, 0xffff);

            /* Select the phase point */
            status |= cs4224_reg_set_channel(slice, CS4224_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL, phsel);

            CS_MDELAY(sweep_duration);
            
            /* Read back the calibration status registers */
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_RXLOCKD0_INTERRUPT, &lockd0);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL1, &cal1);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL2, &cal2);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL3, &cal3);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL4, &cal4);
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE_CAL5, &cal5);

            /* Read back PRBS count */
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count1, &reg_data);
            prbscnt = (cs_uint32)reg_data << 16;
            status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_COMMON_PRBSCHK0_Count0, &reg_data);
            prbscnt |= (cs_uint32)reg_data;
            
            CS_PRINTF(("|%5x|%5x|%4x|%8x|%5x|%4x|%4x|\n", cal1, cal2, cal3, prbscnt, lockd0, cal4, cal5));
        }
    } 

    return status;
}
/* $endif : CORTINA */

/**
* This method runs a BIST test on internal memories
* inside the ASIC. This must be followed by a physical
* reset of the ASIC to return it to an operational state.
*
* This method can be called on multiple slices before
* resetting the ASIC to put it back into operational mode.
*
* @param slice [I] - The slice of the device to run
*                    a BIST test on.
*
* @return CS_OK if the BIST test was successful and
*         CS_ERROR on failure.
*/
cs_status cs4224_diags_mbist_run(cs_uint32 slice)
{
    cs_status status = CS_OK;
    cs_uint16 reg_data1 = 0;
    cs_uint16 reg_data2 = 0;
    cs_int8 attempts = 50;

    /* Trigger the BIST test on both addresses*/
    status |= cs4224_reg_set_channel(slice, CS4224_MSEQ_PS_MBIST_CTRL, 0x3);
    status |= cs4224_reg_set_channel(slice, CS4224_MSEQ_PS_MBIST_CTRL + 0x100, 0x3);

    /* poll first test */
    while(attempts > 0)
    {
        status |= cs4224_reg_get_channel(slice, CS4224_MSEQ_PS_MBIST_STATUS, &reg_data1);

        if( (reg_data1 & CS_BIT0) == 0 )
        {
            CS_MDELAY(1);
            attempts--;
            continue;
        }
        break;
    }
    if(attempts <= 0)
    {
        CS_TRACE(("ERROR: BIST test 1 timed out (register read issue?)\n"));
        status |= CS_ERROR;
    }

    /* poll second test - slightly faster to have two loops (less reg_get calls) */
    attempts = 50;
    while(attempts > 0)
    {
        status |= cs4224_reg_get_channel(slice, CS4224_MSEQ_PS_MBIST_STATUS + 0x100, &reg_data2);

        if( (reg_data2 & CS_BIT0) == 0)
        {
            CS_MDELAY(1);
            attempts--;
            continue;
        }
        break;
    }
    if(attempts <= 0)
    {
        CS_TRACE(("ERROR: BIST test 2 timed out (register read issue?)\n"));
        status |= CS_ERROR;
    }

    /* BIST failed */
    if(reg_data1 & CS_BIT1)
    {
        CS_PRINTF(("\nBIST read error in test 1\n"));
        status |= CS_ERROR;
    }
    if(reg_data2 & CS_BIT1)
    {
        CS_PRINTF(("\nBIST read error in test 2\n"));
        status |= CS_ERROR;
    }

    return status;
}


/** This method will return an error if there are uncorrected FEC blocks on any
 *  slice on the entire device.
 * 
 *  Useful for KR-AN debugging.
 *
 * @param die  [I] - Uses the upper bits to determine which device to get stats from
 *
 * @return CS_OK on a pass, CS_ERROR otherwise
 * 
 * @private
 */
cs_status cs4224_diags_get_fec_errors(
        cs_uint32 die)
{
    cs_status status = CS_OK;
    cs_uint32 upper_bits = die & 0xFFFFFF00;
    cs4224_fec_stats_t fec_stats;
    cs_uint16 i = 0;

    for(i = 0; i < CS4224_MAX_NUM_SLICES(die); i++)
    {
        status |= cs4224_get_fec_stats( (upper_bits | i), &fec_stats );
        /*check for any errors in the FEC stats */
        if( (0 != fec_stats.rx_blk_corr) || (0 != fec_stats.rx_blk_uncorr) )
        {
            CS_PRINTF(( "\nERROR: FEC errors on slice %x. rx_blk_corr = %x    rx_blk_uncorr = %x\n", (upper_bits|i), fec_stats.rx_blk_corr, fec_stats.rx_blk_uncorr ));
            status |= CS_ERROR;
        }
    }

    return status;
}

/** This method will return an error if there are uncorrected FEC blocks on the
 *  particular slice in question.
 *
 * @param slice  [I] - Slice to check the FEC stats on
 *
 * @return CS_OK on a pass, CS_ERROR otherwise
 *
 */
cs_status cs4224_diags_query_fec_status(
        cs_uint32 slice)
{
    cs_status status = CS_OK;
    cs4224_fec_stats_t fec_stats;

    status |= cs4224_get_fec_stats(slice, &fec_stats);
    /*check for any errors in the FEC stats */
    if( (0 != fec_stats.rx_blk_corr) || (0 != fec_stats.rx_blk_uncorr) )
    {
        CS_PRINTF(( "\nERROR: FEC errors on slice %x. rx_blk_corr = %x    rx_blk_uncorr = %x\n", slice, fec_stats.rx_blk_corr, fec_stats.rx_blk_uncorr ));
        status |= CS_ERROR;
    }

    return status;
}


/** This method will clear all the known interrupts.
 *
 *  NOTE: For simplex devices this will only reset either host or line side, even
 *  if there are interrupts on the host side that may have to do with line side
 *  behaviour.
 *
 *  The implementation of this method is not ideal since the list of interrupts is manually maintained.
 *
 *  @param slice [I]  - Slice to reset the interrupts on
 *
 *  @return CS_OK on pass, CS_ERROR otherwise
 * 
 *  @private
 */
cs_status cs4224_diags_clear_interrupts(
    cs_uint32 slice)
{
    cs_status status = CS_OK;
    cs_uint16 interrupts = 0;
    cs_uint16 i = 0, j = 0;

    if(cs4224_is_hw_simplex(slice))
    {
        if(cs4224_line_rx_to_host_tx_dir(slice))
        {
            interrupts = CS4224_STATUS_LINE_INTERRUPT;
        }
        else
        {
            interrupts = CS4224_STATUS_HOST_INTERRUPT;
        }
    }
    else /* duplex */
    {
        interrupts = CS4224_STATUS_LINE_INTERRUPT | CS4224_STATUS_HOST_INTERRUPT;
    }

    /* ideally this should actually just use the irq stuff, but we need a method
     * that can be used even if interrupts are disabled
     */

    /* step through g_edc_fields... */
    for(i = 0; i < sizeof(g_edc_fields)/sizeof(*g_edc_fields); i++)
    {
        /* ignore all non-interrupt rows */
        if(!(interrupts & g_edc_fields[i].include_mask))
        {
            continue;
        }
        /* step through each field in the interrupt row... */
        for(j = 0; j < g_edc_fields[i].cols; j++)
        {
            /* reset the interrupt on this slice */
            /* CS_PRINTF(("addr %x to 0xffff\n", g_edc_fields[i].fields[j].reg_addr)); */
            status |= cs4224_reg_set_channel( slice, g_edc_fields[i].fields[j].reg_addr, 0xFFFF);
        }
    }

    return status;
}

/**
 * This is method used to resync the digital elastic stores of a duplex slice. 
 * 
 * @param slice [I] - The slice to apply the elastic store resync.
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_resync_digital_elsto(
    cs_uint32         slice) 
{
    cs_status status = CS_OK;

    status |= cs4224_resync_elsto(slice, CS4224_PP_LINE_SDS_COMMON_TXELST0_Control);
    status |= cs4224_resync_elsto(slice, CS4224_PP_LINE_SDS_COMMON_RXELST0_Control);
    status |= cs4224_resync_elsto(slice, CS4224_PP_HOST_SDS_COMMON_TXELST0_Control);
    status |= cs4224_resync_elsto(slice, CS4224_PP_HOST_SDS_COMMON_RXELST0_Control);

    return status;
}


/* $if : CORTINA : Only for regression, may add later */
/**
 * This method is used to test the auto-squelch behaviour of a slice.
 * 
 * Private for now, will make public if we really need to
 * 
 * @param slice [I] - The slice to test
 * @param intf  [I] - The side of the slice to test (line/host/splx)
 * 
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @private
 */
cs_status cs4224_diags_validate_auto_squelch_intf(
    cs_uint32 slice,
    e_cs4224_datapath_dir_t intf)
{
    cs_status status = CS_OK;
    cs_uint16 offset = 0;
    e_cs4224_mseq_id mseq_id;
    cs_boolean check = FALSE;
    const cs_char8* rx_side;
    const cs_char8* tx_side;
    cs_uint32 slices[] = {0, 0};
    cs_uint8 slices_len = 0;
    cs_uint8 i = 0;
    cs_uint16 data;
    
    status |= cs4224_get_cfg_side(slice, (e_cs4224_cfg_sides_t*)(&intf));
    if(CS_OK != status)
    {
        return status;
    }
    
    if(CS4224_HOST_RX_TO_LINE_TX_DIR == intf)
    {
        offset = CS4224_LINE_TO_HOST_OFFSET;
        mseq_id = CS4224_DPLX_HOST_MSEQ;
        rx_side = cs4224_translate_cfg_side(CS4224_CFG_HOST_SIDE);
        tx_side = cs4224_translate_cfg_side(CS4224_CFG_LINE_SIDE);
    }
    else
    {
        offset = 0;
        mseq_id = CS4224_DPLX_LINE_MSEQ;
        rx_side = cs4224_translate_cfg_side(CS4224_CFG_LINE_SIDE);
        tx_side = cs4224_translate_cfg_side(CS4224_CFG_HOST_SIDE);
    }
    
    CS_PRINTF(("Check auto squelch on slice %x %s side Rx",slice, rx_side));
    
    status |= cs4224_query_mseq_is_stalled(slice, CS4224_DPLX_HOST_MSEQ, &check);
    if(check)
    {
        CS_TRACE(("\nERROR: MSEQ is stalled on slice %x host side\n", slice));
        return CS_ERROR;
    }
    CS_PRINTF(("."));
    
    status |= cs4224_query_mseq_is_stalled(slice, CS4224_DPLX_LINE_MSEQ, &check);
    if(check)
    {
        CS_TRACE(("\nERROR: MSEQ is stalled on slice %x line side\n", slice));
        return CS_ERROR;
    }
    CS_PRINTF(("."));
    
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB+offset, &data);
    if(CS_IF_CLR(data,CS_BIT2))
    {
        CS_TRACE(("\nERROR: auto squelch not enabled on slice %x %s Rx: 0x%04x\n", slice, rx_side, data));
        return CS_ERROR;
    }
    CS_PRINTF(("."));
    
    /* for duplex slices, figure out which Txs are listening to this slice's squelch requests */
    if(cs4224_is_hw_duplex(slice))
    {
        cs_uint32 other_slice = 0;
        
        if(slice & 0x1)
        {
            other_slice = slice-1;
        }
        else
        {
            other_slice = slice+1;
        }
        
        /* this is used to see if a switch is configured */
        status |= cs4224_reg_get_channel(slice, CS4224_PP_HOST_SDS_DSP_MSEQ_MAIL_SEL-offset, &data);
        if(!data)
        {
            /* this slice's Tx is listening to squelch reqs from this slice */
            slices[slices_len++] = slice;
        }
        
        status |= cs4224_reg_get_channel(other_slice, CS4224_PP_HOST_SDS_DSP_MSEQ_MAIL_SEL-offset, &data);
        if(data)
        {
            /* the other slice's whatever-side Tx is listening to squelch reqs from this slice */
            slices[slices_len++] = other_slice;
        }
    }
    else
    {
        /* no switching for simplex, poor simplex */
        slices[0] = slice;
        slices_len = 1;
    }
    
    status |= cs4224_query_link_ready(slice, mseq_id, 500, &check);
    
    for(i=0; i<slices_len; i++)
    {
        cs_uint32 tmp_slice = (slice & 0xFFFFFF00) | slices[i];
        status |= cs4224_reg_get_channel(tmp_slice, CS4224_PP_HOST_SDS_COMMON_STX0_SQUELCH-offset, &data);
        if(check)
        {
            /* locked */
            if(data == 0x1)
            {
                CS_TRACE(("\nERROR: slice %x %s Tx is squelched even though slice %x %s Rx is locked\n", tmp_slice, tx_side, slice, rx_side));
                return CS_ERROR;
            }
        }
        else
        {
            /* not locked */
            if(data == 0x0)
            {
                CS_TRACE(("\nERROR: slice %x %s Tx is not squelched even though slice %x %s Rx is locked\n", tmp_slice, tx_side, slice, rx_side));
                return CS_ERROR;
            }
        }
        CS_PRINTF(("."));
    }
    
    CS_PRINTF(("auto-squelch behaviour correct!\n"));
    
    return status;
}

/* $endif : CORTINA */

/**
 * This method is a diagnostics method used to disable some portions of the cal
 * 
 * @{warning,
 * There is no going back from this, you need to reconfig the device to reset
 * the config.
 * 
 * This method is not for general usage. It rarely will make sense
 * to do this in a production environment.
 * }
 * 
 * @param slice [I] - The slice
 * @param intf  [I] - The microsequencer to change.
 * @param phsel [I] - The fixed phsel value to use
 * 
 * @return CS_OK on success, CS_ERROR on failure.
 * 
 * @private
 */
cs_status cs4224_diags_set_phsel_mseq(
    cs_uint32        slice,
    e_cs4224_mseq_id mseq,
    cs_uint16        phsel)
{
    cs_status status = CS_OK;
    cs_uint16 offset = 0;
    cs_uint16 reg_data = 0;
    e_cs4224_edc_mode edc_mode = CS_HSIO_EDC_MODE_DISABLED;
    
    offset = cs4224_mseq_get_addr_offset(slice, mseq);
    
    status |= cs4224_query_edc_mode(slice, mseq, &edc_mode);
    if(CS_OK != status)
    {
        return status;
    }
    if(CS_HSIO_EDC_MODE_SR == edc_mode)
    {
        CS_TRACE(("WARNING: Doesn't make sense to set phsel in SR mode, not setting. slice: %x mseq: %d des phsel: 0x%x\n", slice, mseq, phsel));
        return status;
    }
    
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL+offset, &reg_data);
    /*CS_PRINTF(("Previous phsel: 0x%x\n",reg_data));*/

    /* $if : CORTINA : Internal only */
    /* Steps:
     * turn off phsel cal
     * set phsel cal done (trick MSEQ)
     * let the phsel go higher than the mseq wants it to
     * set phsel
     */
    /* $endif : CORTINA */
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB+offset, &reg_data);
    reg_data |= CS_BIT7;
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_LSB+offset, reg_data);
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_MSB+offset, &reg_data);
    reg_data |= CS_BIT13;
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE12_MSB+offset, reg_data);
    
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE15_MSB+offset, &reg_data);
    reg_data |= CS_MSB_BIT31;
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE15_MSB+offset, reg_data);

    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE21_MSB+offset, 0xFF);
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE1_LSB+offset, 0x0);
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE1_MSB+offset, 0xFF);
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE7_LSB+offset, 0x0);
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE7_MSB+offset, 0xFF);
    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_SPARE0_LSB+offset, 0x10);

    status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL+offset, phsel);
    
    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_CAL_RX_PHSEL+offset, &reg_data);
    /*CS_PRINTF(("New phsel: 0x%x\n", reg_data));*/
    if(reg_data != phsel)
    {
        CS_TRACE(("ERROR: phsel not set to desired value, limit reached. Act: %x  des: %x\n",reg_data,phsel));
        return CS_ERROR;
    }
    
    return status;
}




/**
 * This method dumps the microsequencer data-store variables
 * 
 * @param slice  [I] - The slice or port of the device(s) being initialized
 * @param side   [I] - Identifies the microsequencer, line or host
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_dump_data_store(
    cs_uint32 slice, 
    e_cs4224_mseq_id side)
{
    cs_status  status = CS_OK;
    cs_uint16  offset = 0x0000;
    cs_uint16  stall, addr, data0, data1;
    cs_boolean need_to_unstall = FALSE;

    if (side == CS4224_DPLX_HOST_MSEQ)
    {
        CS_PRINTF(("Dumping the HOST side data store of slice %x\n", slice));
        offset = 0x0800;
    }
    else
    {
        CS_PRINTF(("Dumping the LINE side data store of slice %x\n", slice));
    }

    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_OPTIONS_SHADOW + offset, &stall);
    if ((stall & 0x0008) == 0)
    {
        CS_PRINTF(("  Microsequencer is running, stalling it!\n"));

        if (side == CS4224_DPLX_HOST_MSEQ)
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, TRUE);
        }
        else
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, TRUE);
        }
        need_to_unstall = TRUE;
    }

    for (addr = 0; addr < 64; addr++)
    {
        status |= cs4224_reg_set_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_GRAM_CR + offset, 0x8800 | addr);
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_GRAM_D1 + offset, &data1);
        status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_GRAM_D0 + offset, &data0);
        CS_PRINTF(("  addr:%02d, msb:0x%04x, lsb:0x%04x\n", addr, data1, data0));
    }  

    if (need_to_unstall == TRUE) 
    {
        CS_PRINTF(("  Microsequencer was running, un-stalling it!\n"));

        if (side == CS4224_DPLX_HOST_MSEQ)
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, FALSE);
        }
        else
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, FALSE);
        }
    }

    return status;
}

/**
 * This method dumps the microsequencer program-store variables
 * 
 * @param slice  [I] - The slice or port of the device(s) being initialized
 * @param side   [I] - Identifies the microsequencer, line or host
 *
 * @return CS_OK on success, CS_ERROR on failure.
 *
 */
cs_status cs4224_diags_dump_pgrm_store(
    cs_uint32 slice, 
    e_cs4224_mseq_id side)
{
    cs_status  status = CS_OK;
    cs_uint16  offset = 0x0000;
    cs_uint16  stall, addr, data0, data1;
    cs_boolean need_to_unstall = FALSE;
    cs_uint32  die = 0;

    die = cs4224_get_die_from_slice(slice);

    if (side == CS4224_DPLX_HOST_MSEQ)
    {
        CS_PRINTF(("Dumping the HOST side program store of die %x\n", die));
        offset = 0x0800;
    }
    else
    {
        CS_PRINTF(("Dumping the LINE side program store of die %x\n", die));
    }

    status |= cs4224_reg_get_channel(slice, CS4224_PP_LINE_SDS_DSP_MSEQ_OPTIONS_SHADOW + offset, &stall);
    if ((stall & 0x0008) == 0)
    {
        CS_PRINTF(("  Microsequencer is running, stalling it!\n"));

        if (side == CS4224_DPLX_HOST_MSEQ)
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, TRUE);
        }
        else
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, TRUE);
        }
        need_to_unstall = TRUE;
    }

    for (addr = 3584; addr < 4096; addr++)
    {
        status |= cs4224_reg_set(die, CS4224_MSEQ_PS_RAM_CONTROL + offset, 0xa000 | addr);
        status |= cs4224_reg_get(die, CS4224_MSEQ_PS_RAM_DATA1   + offset, &data1);
        status |= cs4224_reg_get(die, CS4224_MSEQ_PS_RAM_DATA0   + offset, &data0);
        CS_PRINTF(("  addr:%02d, data:0x%02x%04x\n", addr, data1, data0));
    }  

    if (need_to_unstall == TRUE) 
    {
        CS_PRINTF(("  Microsequencer was running, un-stalling it!\n"));

        if (side == CS4224_DPLX_HOST_MSEQ)
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_HOST_MSEQ, FALSE);
        }
        else
        {
            cs4224_mseq_stall(slice, CS4224_DPLX_LINE_MSEQ, FALSE);
        }
    }

    return status;
}


