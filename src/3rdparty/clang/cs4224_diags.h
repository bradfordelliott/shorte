/** @file cs4224_diags.h
 ****************************************************************************
 *
 * @brief
 *     This module provides diagnostic methods to assist in debugging
 *     or bringup of the device.
 *
 ****************************************************************************
$copy$
 ***************************************************************************/
#ifndef __CS4224_DIAGS_H__
#define __CS4224_DIAGS_H__

#include "high_level/cs4224.h"
#include "cs4224_registers.h"


#if (CS_HAS_DEBUG_LOOPBACKS == 1)
/**
 * The loopback interface point 
 */
typedef enum
{
    /** No Duplex loopback */
    CS4224_LOOPBK_DUPLEX_NONE       = 0x0,

    /** Digital Near data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_NEAR_DATA */
    CS4224_LOOPBK_DIGITAL_NEAR_DATA = 0x1,

    /** Duplex Near data loopback */
    CS4224_LOOPBK_DUPLEX_NEAR_DATA  = 0x1,

    /** Digital Far data loopback. Deprecated, replaced by CS4224_LOOPBK_DUPLEX_FAR_DATA */
    CS4224_LOOPBK_DIGITAL_FAR_DATA  = 0x2,

    /** Duplex Far data loopback */
    CS4224_LOOPBK_DUPLEX_FAR_DATA   = 0x2,

}e_cs4224_loopback;


/**
 * The loopback interface
 */
typedef enum
{
    /* Loopback on the host interface */
    CS4224_LOOPBK_HOST    = 0x1,

    /* Loopback on the line interface */
    CS4224_LOOPBK_LINE    = 0x3,

}e_cs4224_loopback_interface;


/**
 * This structure is used to store state information
 * that is used when enabling the line or host side duplex
 * near or far loopbacks.
 */
typedef struct
{
    /** initialize flag */
    cs_uint8  initialized;

    /** The state of the SDS_COMMON_STX0_MISC register */
    cs_uint16 stx0_misc;

    /** The state of the line SDS_DSP_MSEQ_POWER_DOWN_LSB register */
    cs_uint16 line_mseq_power_down;

    /** The state of the host SDS_DSP_MSEQ_POWER_DOWN_LSB register */
    cs_uint16 host_mseq_power_down;

    /** The state of the SDS_COMMON_RX0_Config register */
    cs_uint16 rx0_config;

    /** The state of the SDS_COMMON_TX0_Config register */
    cs_uint16 tx0_config;

    /* state of the RXELST0_Control register */
    cs_uint16 rxelst0_control;

    /** The state of the line SDS_COMMON_SRX0_RX_CLKOUT_CTRL register */
    cs_uint16 line_clkout_ctrl;

    /** The state of the host SDS_COMMON_SRX0_RX_CLKOUT_CTRL register */
    cs_uint16 host_clkout_ctrl;

    /** The state of the SDS_COMMON_SRX0_RX_CLKDIV_CTRL register */
    cs_uint16 clkdiv_ctrl;

    /** The state of the SDS_COMMON_RXLOCKD0_CONTROL register */
    cs_uint16 rxlockd0_ctrl;

    /** The state of the LINE_SDS_DSP_MSEQ_SPARE12_LSB register */
    cs_uint16 line_spare12;

    /** The state of the HOST_SDS_DSP_MSEQ_SPARE12_LSB register */
    cs_uint16 host_spare12;

    /** The state of the SDS_DSP_MSEQ_OPTIONS_SHADOW register */
    cs_uint16 mseq_options;

    /** The state of the line EDC mode */
    e_cs4224_edc_mode line_edc_mode;

    /** The state of the host EDC mode */
    e_cs4224_edc_mode host_edc_mode;
    
    /** The state of the SDS_COMMON_SRX0_RX_CPA register */
    cs_uint16 rx_cpa;

}cs4224_diags_duplex_loopback_state_t;


/**
 * This structure is used to store state information
 * that is used when enabling an simplex loopback. 
 */
typedef struct
{
    /** initialize flag */
    cs_uint8  initialized;

    /** The state of the SDS_COMMON_STX0_MISC register */
    cs_uint16 stx0_misc;

    /** The state of the SDS_DSP_MSEQ_POWER_DOWN_LSB register */
    cs_uint16 mseq_power_down;

    /** The state of the SDS_COMMON_SRX0_RX_CONFIG register */
    cs_uint16 rx_config;

    /** The state of the SDS_DSP_MSEQ_SPARE12_LSB register */
    cs_uint16 spare12;

    /** The state of the SDS_COMMON_SRX0_DFE_CONFIG register */
    cs_uint16 dfe_config;

    /** The state of the SDS_COMMON_SRX0_AGC_CONFIG1 register */
    cs_uint16 agc_config1;

}cs4224_diags_simplex_loopback_slice_state_t;


/**
 * This structure is used to store state information
 * that is used when enabling an simplex loopback. 
 */
typedef struct
{
    /** The slice state */
    cs4224_diags_simplex_loopback_slice_state_t slice_state;

    /** The mate slice state */
    cs4224_diags_simplex_loopback_slice_state_t mate_slice_state;

}cs4224_diags_simplex_loopback_state_t;


/* Query the loopback status */
cs_status cs4224_diags_query_loopbacks(
    cs_uint32           slice,
    e_cs4224_loopback*  line_lb_type,
    e_cs4224_loopback*  host_lb_type);

/* $if : CORTINA : Regression testing */
/* Query the loopback status (wrapper) */
cs_status cs4224_diags_query_loopbacks_wrapper(
    cs_uint32           slice,
    cs_uint32           *type);
/* $endif : CORTINA : */

/* Dump the loopback status */
cs_status cs4224_diags_dump_loopbacks(
    cs_uint32  slice);

/* Enable a digital loopback   
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_duplex_loopback_enable 
 *       instead. */
cs_status cs4224_diags_loopback_enable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf);

/* Disable a digital loopback
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_duplex_loopback_disable 
 *       instead. */
cs_status cs4224_diags_loopback_disable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf);

/* Enable a digital loopback
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_duplex_loopback_enable 
 *       instead. */
cs_status cs4224_diags_digital_loopback_enable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf);

/* Disable a digital loopback
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_duplex_loopback_enable 
 *       instead. */
cs_status cs4224_diags_digital_loopback_disable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf);

/* Enable a duplex loopback */
cs_status cs4224_diags_duplex_loopback_enable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf, 
        cs4224_diags_duplex_loopback_state_t* state);

/* Disable a duplex loopback */
cs_status cs4224_diags_duplex_loopback_disable(
        cs_uint32                   slice,
        e_cs4224_loopback           lb_type,
        e_cs4224_loopback_interface intf, 
        cs4224_diags_duplex_loopback_state_t* state);

/* Enable an analog loopback
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_simplex_loopback_enable 
 *       instead. */
cs_status cs4224_diags_analog_loopback_enable(
        cs_uint32   slice);

/* Disable an analog loopback
 * NOTE: This method has been deprecated, 
 *       use cs4224_diags_simplex_loopback_disable 
 *       instead. */
cs_status cs4224_diags_analog_loopback_disable(
        cs_uint32   slice);

/* Enable a simplex loopback */
cs_status cs4224_diags_simplex_loopback_enable(
        cs_uint32                             slice,
        cs4224_diags_simplex_loopback_state_t* state);

/* Disable a simplex loopback */
cs_status cs4224_diags_simplex_loopback_disable(
        cs_uint32                             slice,
        cs4224_diags_simplex_loopback_state_t* state);

#if 0
/* This method saves the original state of the interface
 * and is called when enabling the line or host side digital loopback. */
cs_status cs4224_diags_loopback_save_state(
    cs_uint32                             slice, 
    e_cs4224_loopback_interface           intf,
    cs4224_diags_digital_loopback_state_t *state);
#endif


/* $if : CORTINA : Only for regression right now */
void cs4224_diags_debug_loopback_test(
        cs_uint32 die);

void cs4224_diags_simplex_loopback_dump_state(
        cs4224_diags_simplex_loopback_state_t* state);

void cs4224_diags_duplex_loopback_dump_state(
        cs4224_diags_duplex_loopback_state_t* state);

/* $endif : CORTINA : */

#endif /* CS_HAS_DEBUG_LOOPBACKS == 1 */


#if (CS_HAS_DEBUG_PRBS == 1)
/**
 * The supported PRBS polynomials 
 */
typedef enum
{
    /** 1 + x^28 + x^31  */
    CS4224_PRBS_Tx_2exp31 = 0x0,

    /** 1 + x^18 + x^23  */
    CS4224_PRBS_Tx_2exp23 = 0x1,
    
    /** 1 + x^14 + x^15  */
    CS4224_PRBS_Tx_2exp15 = 0x2,

    /** 1 + x^6 + x^7  */
    CS4224_PRBS_Tx_2exp7 = 0x3,
    
    /** 1 + x^4 + x^9  */
    CS4224_PRBS_Tx_2exp9 = 0x4,

    /** 1 + x^5 + x^9  */
    CS4224_PRBS_Tx_2exp9_5 = 0x5,

    /** 1 + x^5 + x^58  */
    CS4224_PRBS_Tx_2exp58 = 0x6,

}e_cs4224_prbs_polynomial;


/**
 * Used to select the PRBS generator/checker
 * pair
 */
typedef enum
{
    /** The line side PRBS generator/checker */
    CS4224_PRBS_LINE_INTERFACE  = 0,

    /** The host side PRBS generator/checker. */
    CS4224_PRBS_HOST_INTERFACE  = 1,

    /** If in simplex mode this automatically
     * determines the appropriate checker or generator */
    CS4224_PRBS_SIMPLEX_INTERFACE = 2,

}e_cs4224_prbs_interface;


/** PRBS error injection modes */
typedef enum
{
    /** Inject continuous errors - autopolarity must be disabled */
    CS4224_PRBS_INJECT_ERROR_CONTINUOUS = 0x8,

    /** Inject continuous single bit errors */
    CS4224_PRBS_INJECT_ERROR_ONE_BIT_CONTINUOUS = 0x4,

    /** Inject a single error once */
    CS4224_PRBS_INJECT_ERROR_ONCE = 0x2,

    /** Inject a single bit error once */
    CS4224_PRBS_INJECT_ERROR_ONE_BIT_ONCE = 0x1
}e_cs4224_prbsgen_error_cfg;


/* Configure the PRBS generator for transmit  */
cs_status cs4224_diags_prbs_generator_config(
        cs_uint32                slice,
        e_cs4224_prbs_interface  prbs_sel,
        e_cs4224_prbs_polynomial polynomial,
        cs_uint8                 invert);

/* Enable or disable the PRBS generator  */
cs_status cs4224_diags_prbs_generator_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint8                enable);

/* Inject errors via the PRBS generator */
cs_status cs4224_diags_prbs_generator_set_error_ctrl(
    cs_uint32                  slice,
    e_cs4224_prbs_interface    prbs_sel,
    e_cs4224_prbsgen_error_cfg mode,
    cs_boolean                 enable);

/* Configure the PRBS checker for receiving a test pattern and verifying it is correct. 
 *  */
cs_status cs4224_diags_prbs_checker_config(
        cs_uint32                  slice,
        e_cs4224_prbs_interface    prbs_sel,
        e_cs4224_prbs_polynomial   polynomial,
        cs_uint8                   invert, 
        cs_uint8                   lbk_enable);

/* Enable or disable the PRBS checker  */
cs_status cs4224_diags_prbs_checker_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint8                enable);

/* Enable or disable the PRBS checker auto-polarity */
cs_status cs4224_diags_prbs_checker_autopol_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              enable);

/* If auto-polarity is enabled, gets the current inverted state of the signal */
cs_status cs4224_diags_prbs_checker_get_polarity(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              *inverted);

/* Retrieves the 32 bit error count reported by the PRBS checker.  */
cs_status cs4224_diags_prbs_checker_get_errors(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint32*              error_count);

/* Retrieve the full status of the PRBS checker including RX lock,
 * sync detect and error count */
cs_status cs4224_diags_prbs_checker_get_status(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_uint32*              error_count,
        cs_boolean*             prbs_sync);

/* This method is called to configure the pattern that the fix pattern generator 
 * transmits.  */
cs_status cs4224_diags_fix_ptrn_generator_cfg(
        cs_uint32               slice,
        e_cs4224_prbs_interface gen_sel,
        cs_uint32               sequence_a,
        cs_uint8                repeat_a,
        cs_uint32               sequence_b,
        cs_uint8                repeat_b);

/* Enable or disable the fixed pattern generator  */
cs_status cs4224_diags_fix_ptrn_generator_enable(
        cs_uint32               slice,
        e_cs4224_prbs_interface prbs_sel,
        cs_boolean              enable);

/* Set the PRBS generator in Local timing/PFD mode */
cs_status cs4224_diags_prbs_generator_set_pfd_mode(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              enable);

/* Set the PRBS generator in Local timing/PFD mode */
cs_status cs4224_diags_prbs_generator_set_local_timing_mode(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              enable);

/* Enable or disable squelching of the generated PRBS pattern */
cs_status cs4224_diags_prbs_generator_squelch(
    cs_uint32               slice,
    e_cs4224_prbs_interface prbs_sel,
    cs_boolean              squelch);

#endif /* CS_HAS_DEBUG_PRBS == 1 */

/*
+=========================================
| Status Dump Methods
+=========================================
*/
#if (CS_HAS_DEBUG_STATUS_DUMPS == 1)

cs_status cs4224_diags_switch_show_state(
    cs_uint32 slice);

/* Show the VCO lock status summary
 * NOTE: This method has been deprecated, use cs4224_diags_show_vco_status 
 *       instead. */
void cs4224_diags_show_vco_lock_status(void);

/* Show the VCO status with a prefix */
void cs4224_diags_show_vco_status_prefixed(
    cs_uint32   slice,
    const char* prefix);

/* Show the VCO lock status summary of an ASIC */
void cs4224_diags_show_vco_status(
    cs_uint32 slice);

/* Show the VCO lock status summary in a string
 * NOTE: This method has been deprecated, use cs4224_diags_get_vco_status_string 
 *       instead. */
void cs4224_diags_get_vco_lock_status_string(
    char* buffer);

/* Show the VCO lock status summary of an ASIC in a string */
const char* cs4224_diags_get_vco_status_string(
    cs_uint32 slice,
    char* buffer);

/* $if : CORTINA : Regression testing */
char* cs4224_diags_get_vco_status_string_wrapper(
    cs_uint32 slice);
/* $endif : CORTINA */

void cs4224_diags_is_vco_locked(
    cs_uint32 slice,
    cs4224_vco_lock_status_t *vco);



/* Sections in the status summary report */

/**
 * A status flag used with cs4224_diags_show_status() to
 * display sections in the summary report
 */
typedef enum
{
    /**
     * display the global status/config in the summary report
     */
    CS4224_STATUS_GLOBAL = 1 << 0,

    /**
     * display the SERDES locking information in the summary report
     */
    CS4224_STATUS_SERDES = 1 << 1,

    /**
     * display the Microsequencer status in the summary report
     */
    CS4224_STATUS_MSEQ = 1 << 2,

    /**
     * display the clocking configuration in the summary report
     */
    CS4224_STATUS_CLOCKING = 1 << 3,

    /**
     * display the line interrupts
     */
    CS4224_STATUS_LINE_INTERRUPT = 1 << 4,
    
    /**
     * display the host interrupts
     */
    CS4224_STATUS_HOST_INTERRUPT = 1 << 5,

    /**
     * The link status (including RX Lock, EDC Convergence and PCS)
     */
    CS4224_STATUS_LINK = 1<<6,
    
    /**
     * display everything
     */
    CS4224_STATUS_ALL = 0xffff,
}e_cs4224_status_mask;

/* This method displays a status summary of the device */
cs_status cs4224_diags_show_status(
    cs_uint32 slice_start,
    cs_uint32 slice_end,
    cs_uint16 sections_to_display);

/* Dump and clear interrupts and FEC stats */
cs_status cs4224_diags_show_and_clear_stats(cs_uint32 die);


#endif /* CS_HAS_DEBUG_STATUS_DUMPS == 1 */


#if (CS_HAS_DEBUG_REGISTER_DUMPS == 1)

/* Check to see if a register can be read or not */
cs_boolean cs4224_diags_register_can_read(
        cs_uint16 addr);

/* $if : CORTINA : for internal stuff */
/* A test harness to validate the dump range method */
cs_status cs4224_diags_register_dump_range_wrapper(
    cs_uint32 die,
    cs_uint32 start_addr,
    cs_uint32 end_addr);
/* $endif : CORTINA */

/* Perform a register dump of all slices by calling CS_PRINTF()
 * NOTE: This method has been deprecated, use cs4224_diags_register_dump_asic 
 *       instead. */
void cs4224_diags_register_dump(void);

/* Perform a register dump of all slices of a selected ASIC by calling CS_PRINTF() */
void cs4224_diags_register_dump_asic(
    cs_uint32 slice);

void cs4224_diags_register_dump_die(
    cs_uint32 die);

/* Read a range of registers for a particular slice */
cs_status cs4224_diags_register_dump_range(
        cs_uint32 die,
        cs_uint32 start_addr,
        cs_uint32 end_addr,
        cs_uint16 registers[]);

#endif /* CS_HAS_DEBUG_REGISTER_DUMPS == 1 */

/* Diagnostic method to sweep the calibration parameters for performance analysis */
cs_status cs4224_diags_sweep_calibration_parameters(
    cs_uint32 slice_start,
    cs_uint32 slice_end,
    cs_uint32 sweep_duration);

/* Diagnostic method to perform an automated memory BIST test */
cs_status cs4224_diags_mbist_run(cs_uint32 slice);

/* Returns CS_ERROR if there are FEC errors on any slice */
cs_status cs4224_diags_get_fec_errors(
        cs_uint32 die);

/* Returns CS_ERROR if there are FEC errors on a single slice */
cs_status cs4224_diags_query_fec_status(
        cs_uint32 slice);

/* Clear all the interrupts */
cs_status cs4224_diags_clear_interrupts(
    cs_uint32 slice);

/* Re-sync the digital elastic store */
cs_status cs4224_diags_resync_digital_elsto(
    cs_uint32 slice);

/* Dump the contents of a microsequencer data store */
cs_status cs4224_diags_dump_data_store(
    cs_uint32 slice, 
    e_cs4224_mseq_id side);

/* Dump the contents of a microsequencer program store */
cs_status cs4224_diags_dump_pgrm_store(
    cs_uint32 slice, 
    e_cs4224_mseq_id side);

/* $if : CORTINA : Only for regression, may add later */
cs_status cs4224_diags_validate_auto_squelch_intf(
    cs_uint32 slice,
    e_cs4224_datapath_dir_t intf);
/* $endif : CORTINA */

#endif /* __CS4224_DIAGS_H__ */
