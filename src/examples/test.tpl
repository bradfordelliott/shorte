@c
/** @file leeds_macsec.c
****************************************************************************
 *
 * @brief        
 *    This module provides the application layer with the routines necessary 
 *    to configure the MACsec block.
 *
 ******************************************************************************
 * @author
 * Copyright 2010 by Cortina Systems. All text contained within remains property
 * of Cortina Sytems corporation and may not be modified, distributed, or
 * reproduced without the express written permission of Cortina Systems
 *
 *****************************************************************************/

#include <stdio.h>
#include <memory.h>

#if defined(OS_WINDOWS)
#    pragma warning( disable : 4716 )
#    pragma warning( disable : 4244 )
#endif /* OS_WINDOWS */

#include "leeds_hal.h"

#include "leeds_types.h"
#include "leeds_macsec.h"
#include "leeds_macsec_types_internal.h"
#include "leeds_register_map.h"



#if defined(DEBUG)
#    define DEBUG_TABLE_HEADER(fd) \
        dbg_dump(fd, "00000000001111111111222222222233333333334444444444555555555566666666667777777777\n"); \
        dbg_dump(fd, "01234567890123456789012345678901234567890123456789012345678901234567890123456789\n");
#else
#    define DEBUG_TABLE_HEADER(fd)
#endif /* DEBUG */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to intialize the SafeNet SafeXcel-IP_60 MACsec ingress and egress cores. 
 * Note, this method must only be called on start-up because the MACsec core registers must 
 * not be changed during normal operations. This method assumes that the ingress and egress 
 * flows are symmetrical, for example, MACsec enabled on both ingress and egress.
 *
 *  @param port   [I] -  The port number of the device to access.
 *  @return           -  CS_OK or CS_ERROR.
 *
 */
cs_status leeds_macsec_init(uint32 port)
{
    cs_status                          status;
    uint8                              entry;
    leeds_macsec_core_ctxt_tok_ctrl_t  core_ctxt_tok_ctrl;
    leeds_macsec_core_ctxt_prot_al_t   core_ctxt_prot_al;
    leeds_macsec_core_ctxt_frm_eng_t   core_ctxt_frm_eng;
    leeds_macsec_core_ctxt_t           core_ctxt = {0};
    leeds_macsec_ctxt_rec_t            ctxt[NUM_MACSEC_ICT_ENTRIES] = 
      {{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}; 
    leeds_macsec_token_t               token[NUM_MACSEC_IRT_ENTRIES] = 
      {{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},  
       {0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}; 

    /* 
    Initialize the MACsec core for both ingress and egress  
    */

    /* 
    must write zeroes to all Token and Context memories otherwise interrupt may
    occur when reading from un-initialized memory
    */
    status = leeds_macsec_ict_tbl_wr( port, 0, NUM_MACSEC_ICT_ENTRIES, &ctxt[0]);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ict_tbl_wr() returned status:%d\n", status);
      return status;
    } 
    status = leeds_macsec_ect_tbl_wr( port, 0, NUM_MACSEC_ICT_ENTRIES, &ctxt[0]);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ect_tbl_wr() returned status:%d\n", status);
      return status;
    } 

    status = leeds_macsec_irt_tbl_wr( port, 0, 32, &token[0]);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_irt_tbl_wr() returned status:%d\n", status);
      return status;
    } 
    status = leeds_macsec_ert_tbl_wr( port, 0, 32, &token[0]);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ert_tbl_wr() returned status:%d\n", status);
      return status;
    } 

    /* Token Control and Status */
    core_ctxt_tok_ctrl.regs.reg             = 0;
    core_ctxt_tok_ctrl.fields.int_puls_lvl  = 1;
    core_ctxt_tok_ctrl.fields.debug_mode    = 0;
    core_ctxt_tok_ctrl.fields.proc_n_frames = 0;
    core_ctxt_tok_ctrl.fields.hold_proc     = 0;

    /* Protocol & Algorithm enable */
    core_ctxt_prot_al.regs.reg            = 0;
    core_ctxt_prot_al.fields.auth_only    = 1;
    core_ctxt_prot_al.fields.enc_only     = 1;
    core_ctxt_prot_al.fields.auth_enc     = 1;
    core_ctxt_prot_al.fields.auth_dec     = 1;
    core_ctxt_prot_al.fields.enc_auth     = 1;
    core_ctxt_prot_al.fields.dec_auth     = 1;
    core_ctxt_prot_al.fields.key_128b     = 1;
    core_ctxt_prot_al.fields.aes_ctr_icm  = 1;
    core_ctxt_prot_al.fields.gcm_hash     = 1;

    /* Context control */
    /*
    in the Frame Engine Context Control registers, configure the Context Control Register to
    control mode where the context size is 16 dwords (or 64 bytes)
    */
    core_ctxt_frm_eng.regs.reg                   = 0;
    core_ctxt_frm_eng.fields.ctxt_ctrl_ctxt_size = 16;
    core_ctxt_frm_eng.fields.ctxt_ctrl_addr_mode = 0;
    core_ctxt_frm_eng.fields.ctxt_ctrl_ctrl_mode = 1;

    core_ctxt.ctxt_control   = core_ctxt_frm_eng.regs.reg;
    core_ctxt.prot_al_enb    = core_ctxt_prot_al.regs.reg;
    core_ctxt.token_ctl_stat = core_ctxt_tok_ctrl.regs.reg; 

    leeds_macsec_icc_wr(port, 0, &core_ctxt);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_icc_wr() returned status:%d\n", status);
      return status;
    } 

    leeds_macsec_ecc_wr(port, 0, &core_ctxt);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ecc_wr() returned status:%d\n", status);
      return status;
    } 

    /*
    setup some default frame validation 
    */

    status = leeds_macsec_frame_validation_mode(port, e_leeds_macsec_ingress_controlled, e_leeds_macsec_non_strict);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode() returned status:%d\n", status);
      return status;
    } 
    status = leeds_macsec_frame_validation_mode(port, e_leeds_macsec_ingress_un_controlled, e_leeds_macsec_non_strict);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode() returned status:%d\n", status);
      return status;
    } 
    status = leeds_macsec_frame_validation_mode(port, e_leeds_macsec_ingress_invalid_frame, e_leeds_macsec_non_strict);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode() returned status:%d\n", status);
      return status;
    } 
    status = leeds_macsec_frame_validation_mode(port, e_leeds_macsec_egress_security_miss, e_leeds_macsec_non_strict);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode() returned status:%d\n", status);
      return status;
    } 

    /* configure bypass for event (rule miss) on both data and control-plane frames */
    /* note: the miss rule is global ie applies to all ingress security flows */

    status = leeds_macsec_ingress_cc_default_action(port,
                                            0, /* entry not used for miss event */
                                            e_leeds_macsec_cc_miss,
                                            e_leeds_macsec_cc_non_control,
                                            e_leeds_macsec_cc_bypass);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action() returned status:%d\n", status);
      return status;
    } 

    status = leeds_macsec_ingress_cc_default_action(port,
                                            0, /* entry not used for miss event */
                                            e_leeds_macsec_cc_miss,
                                            e_leeds_macsec_cc_control,
                                            e_leeds_macsec_cc_bypass);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action() returned status:%d\n", status);
      return status;
    } 

    /* configure bypass for event (rule hit) on both data and control-plane frames */
    /* note: the hit rule is per entry ie applies to individual ingress security flows */
    for (entry=0; entry<16; entry++)
    {
      status = leeds_macsec_ingress_cc_default_action(port,
                                              entry,
                                              e_leeds_macsec_cc_hit,
                                              e_leeds_macsec_cc_control,
                                              e_leeds_macsec_cc_bypass);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action() returned status:%d\n", status);
        return status;
      } 

      status = leeds_macsec_ingress_cc_default_action(port,
                                              entry,
                                              e_leeds_macsec_cc_hit,
                                              e_leeds_macsec_cc_non_control,
                                              e_leeds_macsec_cc_bypass);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action() returned status:%d\n", status);
        return status;
      } 
    }

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to configure an egress flow.
 *
 *  @param port       [I] -  The port number of the device to access.
 *  @param cam_entry  [I] -  The entry index within the TCAM to program (range 0-31) .
 *  @param setup      [I] -  The configuration info to program the flow. Refer to the 
 *                           leeds_macsec_egress_setup_flow_t data structure for the layout 
 *                           of the data. 
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */
cs_status leeds_macsec_egress_setup_flow_entry(uint32 port, uint32 cam_entry, 
                                               leeds_macsec_egress_setup_flow_t *setup)
{
    leeds_macsec_epr_cam_entry_t cam;         /* egress classifier/parser entry */
    leeds_macsec_epr_cam_mask_t  mask;        /* egress classifier/parser mask */
    leeds_macsec_ctxt_rec_t      ctxt;        /* egress context memory, see Table 16, page 65 */
    leeds_macsec_token_t         rule;        /* egress token memory, see page 53 */
    int                          i;
    uint8                        *ptr1, *ptr2;
    e_leeds_macsec_hw_commit     hw_commit = e_leeds_macsec_hw_commit_none;
    cs_status                    status;
    uint16                       ctxt_entry;
    leeds_macsec_ctxt_ctrl_t     ctxt_ctrl;

    if(cam_entry >= NUM_MACSEC_EPR_CAM_ENTRIES)
    {
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_setup_flow_entry(), cam_entry >= NUM_MACSEC_EPR_CAM_ENTRIES, cam_entry:%d\n", cam_entry);
        return CS_BOUNDS;
    }

    /* clear the structures */
    memset(&cam,  0, sizeof(cam));
    memset(&mask, 0, sizeof(mask));
    memset(&ctxt, 0, sizeof(ctxt));
    memset(&rule, 0, sizeof(rule));

    /* Setup the epr TCAM entries */
    cam.vlan    = setup->parser.fields.vlan;
    cam.et      = setup->parser.fields.etype; 

    ptr1 = (uint8 *)&setup->parser.fields.sa;
    ptr2 = (uint8 *)&setup->parser.fields.da;
    for(i=0;i<6;i++) {
      cam.sa[i] = *ptr1++;     
      cam.da[i] = *ptr2++;
    }

    /* Setup the epr TCAM masks */
    mask.vlan    = setup->parser.fields.vlan_mask;
    mask.et      = setup->parser.fields.etype_mask;
    mask.sa      = setup->parser.fields.sa_mask;
    mask.da      = setup->parser.fields.da_mask;

    hw_commit |= e_leeds_macsec_hw_commit_parser;

    /* 
    lets setup the egress Token rules according to the flow type
    */
    switch (setup->rule.fields.action) {

      case e_leeds_macsec_authenticate_decrypt: /* only valid on ingress */
        break;

      case e_leeds_macsec_drop:
      case e_leeds_macsec_bypass:

        rule.token_type  = LEEDS_MACSEC_BYPASS_DROP_CRYPT_AUTH_TOKEN;
        rule.scb         = 1; /* shared with the C field in special token */
        rule.oid_valid   = 1; /* the ouput identifier word is part of the token */
        if (e_leeds_macsec_drop == setup->rule.fields.action)
        {
          rule.output_id = 0x80000000; /* IOD set to drop */
        }
        else 
        {
          rule.output_id = 0x40000000; /* IOD set to bypass */
        }
        hw_commit |= e_leeds_macsec_hw_commit_rule;
        break;

      case e_leeds_macsec_authenticate_encrypt:
      case e_leeds_macsec_authenticate_only:
        /* this is a MACsec flow, note SW does not care about the difference between 
           auth-encrypt and auth-only. */

        rule.token_type  = LEEDS_MACSEC_MACSEC_TOKEN; /* MACsec enable */
        rule.pass        = 0; /* force to 0 on egress */
        rule.direction   = 0; /* egress */
        rule.es          = setup->rule.fields.sectag_option_es; 
        rule.sc          = setup->rule.fields.sectag_option_sc; 
        rule.scb         = setup->rule.fields.sectag_option_scb;
        rule.too         = 1; /* append encrypted ICV to the frame */

        if (30 == setup->sa_ctxt.fields.ctrl_co_offset) {
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 1; /* select 30 byte co offset */
        } else if (50 == setup->sa_ctxt.fields.ctrl_co_offset) {
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 2; /* select 50 byte co offset */
        } else if ((0 < setup->sa_ctxt.fields.ctrl_co_offset) && 
                  (128 > setup->sa_ctxt.fields.ctrl_co_offset)) {
          /* make use of the ext co offset word in token, note: we are forcing the
             header offset field to 0 
          */
          rule.eco         = 1; /* enable extended co offset */
          rule.co          = 2; /* select 50 byte co offset */
          rule.extended_co = setup->sa_ctxt.fields.ctrl_co_offset << 24;
        }
        else {
          /* no co offsets or co offset too large */
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 0; /* no co offset */
        }
        rule.cid_update  = 1; /* always update context id internally */
        rule.oid_valid   = 0; /* the ouput identifier word is part of the token */
        rule.len_valid   = 0; /* We are always in cut-through mode, set to 0 */ 
        rule.inp_pkt_len = 0; /* always in cut-through mode, set to 0 */
        
        /* lets build the Output Id word */
        rule.output_id   = 0;
        if (TRUE == setup->rule.fields.loopback_to_ingress) {
          rule.output_id |= (0x1 << 29); /* enable loopback to ingress */
        }

        /*
        Note to remember: TCAM, Token entries are mapped 1 to 1, but not the 
        Context records. 
        We must find an available Context record, rifle thru all 16 Context records
        looking for one with ToP field set to 0, don't forget to assign it to rule.context_ptr 
        and also ctxt.ctxt_id  
        Context pointer points to a valid context (range 0..16). Since context records
        are of size 0x40 words, pointer for 0th Context : 0x0 , 1st Context:0x40, 
        2nd Context : 0x80.etc 
        */
        status = leeds_macsec_egress_find_free_ctxt_entry(port, &ctxt_entry);
        if (CS_OK != status)
        {
          /* no free entries, perhaps this is the 17th encryption flow! */
          dbg_dump(stdout, "ERROR: leeds_macsec_egress_find_free_ctxt_entry() returned status:%d\n", status);
          return status;
        }

        rule.context_ptr = ctxt_entry * 0x40; 
        rule.output_id   = 0;   /* ?? must configure this word */

        hw_commit |= e_leeds_macsec_hw_commit_rule;
        break;

      default:
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_setup_flow_entry(), invalid setup->rule.fields.action:%d\n", 
                 setup->rule.fields.action);
        return CS_ERROR;
        break;

    } /* case */

    /* 
    lets setup the egress context record if MACsec flow
    */
    switch (setup->rule.fields.action) {
      case e_leeds_macsec_drop:                 /* context record not required */
      case e_leeds_macsec_bypass:               /* context record not required */
        break;

      case e_leeds_macsec_authenticate_encrypt:
      case e_leeds_macsec_authenticate_only:

        /* only update the Context record when flow is MACsec */
        /* build up the control word in the context record */
        ctxt_ctrl.fields.top          = 6; /* always 6 for egress */ 
        ctxt_ctrl.fields.pack_b_op    = 0; /* used for debug, force to 0 */
        ctxt_ctrl.fields.iv01         = 1; /* IV0 present */
        ctxt_ctrl.fields.iv02         = 1; /* IV1 present */ 
        ctxt_ctrl.fields.iv03         = 0; /* IV3 field never used, force to 0 */
        ctxt_ctrl.fields.ct_len       = 0; /* used for debug, force to 0 */
        ctxt_ctrl.fields.up_seq_num   = 1; /* always update the seq number in ext memory */
        ctxt_ctrl.fields.iv_format    = 1; /* full IV mode */
        ctxt_ctrl.fields.encrypt_auth = 1; /* encrypt authent result into ICV */            
        ctxt_ctrl.fields.key          = 1; 
        ctxt_ctrl.fields.an           = setup->sa_ctxt.fields.ctrl_assoc_num; /* association num */
        ctxt_ctrl.fields.crypto_al    = 5; /* always enable AES-128 crypto algorithm */
        ctxt_ctrl.fields.digest_type  = 2; /* single authentication key */
        ctxt_ctrl.fields.authent_al   = 4; /* always enable GHASH authentication algorithm */
        ctxt_ctrl.fields.seq_type     = 1; /* 32 bit seq_num present in ctxt record */
        ctxt_ctrl.fields.ctxt_id      = 1; /* ctxt id present in ctxt record, this must enabled */ 

        if (TRUE == setup->sa_ctxt.fields.ctrl_replay_window) {
          /* if Replay Window Feature is enabled then turn it on and stuff the mask in seq_num_mask */
          ctxt_ctrl.fields.seq_mask = 1; /* seq mask present in ctxt record */
          ctxt.seq_num_mask  = setup->sa_ctxt.fields.seq_num_mask;
 
        } else {
          ctxt_ctrl.fields.seq_mask = 0; /* seq mask not present in ctxt record */
        }

        ctxt.ctrl_word = ctxt_ctrl.regs.reg;

        ctxt.seq_num = setup->sa_ctxt.fields.seq_num; /* (packet_num) */
 
        for(i=0;i<16;i++) {
          ctxt.akey[i] = setup->sa_ctxt.fields.aes_key[i]; /* watch out for endian-ness */
          ctxt.hkey[i] = setup->sa_ctxt.fields.ghash_key[i];
        }

        ctxt.iv0 = setup->sa_ctxt.fields.iv0; /* SCI[31:0 ] */
        ctxt.iv1 = setup->sa_ctxt.fields.iv1; /* SCI[63:32] */

        ctxt.ctxt_id = ctxt_entry * 0x40; /* points to itself */

        hw_commit |= e_leeds_macsec_hw_commit_ctxt;
        break;

      case e_leeds_macsec_authenticate_decrypt: /* only valid on ingress */

      default:
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_setup_flow_entry(), invalid setup->rule.fields.action:%d\n", 
                 setup->rule.fields.action);
        return CS_ERROR;
        break;

    } /* case */

    /*
    Update the various options for tag parsing using MACSEC_EGRESS_TAG_CONTROL
    they are: default_up[2:0], 
              use_inner_tag, 
              parse_802dot1q, 
              parse_802dot1s,
              parse_QinQ      
    */

    /*
    To change the default priority (for the frame's 802.1q PCP fields), update the mapping table in 
    MACSEC_EGRESS_R802DOT1Q_TAG_MAP0..1
    */

    /* 
    Specify 1 of 3 ethertypes (for the 802.1s tag frame), update MACSEC_EGRESS_R802DOT1S_TAG_ET0..2
    */

    /* if all is good, program the records to the h/w */
    if ((hw_commit & e_leeds_macsec_hw_commit_parser) && (hw_commit & e_leeds_macsec_hw_commit_rule))
    {
      status = leeds_macsec_epr_cam_wr(port, cam_entry, &cam, &mask);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_epr_cam_wr() returned status:%d\n", status);
        return status;
      } 
      status = leeds_macsec_ert_wr(port, cam_entry, &rule);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ert_wr() returned status:%d\n", status);
        return status;
      } 
      /* context record updates are optional */
      if (hw_commit & e_leeds_macsec_hw_commit_ctxt) 
      {
        status = leeds_macsec_ect_wr(port, ctxt_entry, &ctxt);
        if (CS_OK != status)
        {
          dbg_dump(stdout, "ERROR: leeds_macsec_ect_wr() returned status:%d\n", status);
          return status;
        } 
        /*
        Update table to map ctxt index to SA's for stats purposes
        */
        status = leeds_macsec_egress_update_sa_map(port, cam_entry, ctxt_entry, TRUE);
        if (CS_OK != status)
        {
          dbg_dump(stdout, "ERROR: leeds_macsec_egress_update_sa_map() returned status:%d\n", status);
          return status;
        } 
      }

      /* The last step is to enable the TCAM entry valid bit */
      status = leeds_macsec_egress_update_cam_entry_valid(port, cam_entry, TRUE);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_update_cam_entry_valid() returned status:%d\n", status);
        return status;
      } 
    } 
    return CS_OK;

} /* leeds_macsec_egress_setup_flow_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to configure an ingress flow.
 *
 *  @param port       [I] -  The port number of the device to access.
 *  @param cam_entry  [I] -  The entry index within the TCAM to program (range 0-31).
 *  @param setup      [I] -  The configuration info to program the flow. Refer to the 
 *                           leeds_macsec_ingress_setup_flow_t data structure for the layout 
 *                           of the data. 
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_setup_flow_entry(uint32 port, uint32 cam_entry, 
                                                leeds_macsec_ingress_setup_flow_t *setup)
{
    leeds_macsec_ipr_cam_entry_t cam   = {0};
    leeds_macsec_ipr_cam_mask_t  mask  = {0};
    leeds_macsec_ctxt_rec_t      ctxt  = {0};
    leeds_macsec_token_t         rule  = {0};
    int                          i;
    uint8                        *ptr1, *ptr2;
    e_leeds_macsec_hw_commit     hw_commit = e_leeds_macsec_hw_commit_none;
    cs_status                    status;
    uint16                       ctxt_entry;
    leeds_macsec_ctxt_ctrl_t     ctxt_ctrl;

    if(cam_entry >= NUM_MACSEC_IPR_CAM_ENTRIES)
    {
        dbg_dump(stdout, "ERROR: cam_entry >= NUM_MACSEC_IPR_CAM_ENTRIES, cam_entry:%d\n", cam_entry);
        return CS_BOUNDS;
    }

    /* clear the structures */
    memset(&cam,  0, sizeof(cam));
    memset(&mask, 0, sizeof(mask));
    memset(&ctxt, 0, sizeof(ctxt));
    memset(&rule, 0, sizeof(rule));

    /* Setup the ipr TCAM entries */
    cam.fe     = setup->parser.fields.from_e; /* what does this do */
    cam.et     = setup->parser.fields.etype;
    cam.tci_an = setup->parser.fields.tci_an;
    cam.sci    = setup->parser.fields.sci;

    /*
    Q: shoud we care about sa,da, on ingress cisco doesn't 
    */
    ptr1 = (uint8 *)&setup->parser.fields.sa;
    ptr2 = (uint8 *)&setup->parser.fields.da;
    for(i=0;i<6;i++) {
      cam.sa[i] = *ptr1++;     
      cam.da[i] = *ptr2++;
    }

    /* Setup the ipr TCAM masks */
    mask.fe     = setup->parser.fields.from_e_mask; /* not needed */
    mask.et     = setup->parser.fields.etype_mask;
    mask.tci_an = setup->parser.fields.tci_an_mask;

    mask.sci    = setup->parser.fields.sci_mask;
    mask.sa     = setup->parser.fields.sa_mask; /* not needed */
    mask.da     = setup->parser.fields.da_mask; /* not needed */

    hw_commit |= e_leeds_macsec_hw_commit_parser;

    /* 
    lets setup the ingress Token rules according to the flow type
    */
    switch (setup->rule.fields.action) {

      case e_leeds_macsec_authenticate_encrypt:   /* only valid on egress */
      case e_leeds_macsec_authenticate_only:      /* only valid on egress */
        break;

      case e_leeds_macsec_drop:
      case e_leeds_macsec_bypass:

        rule.token_type  = LEEDS_MACSEC_BYPASS_DROP_CRYPT_AUTH_TOKEN;
        rule.scb         = 1; /* shared with the C field in special token */
        rule.oid_valid   = 1; /* the ouput identifier word is part of the token */
        if (e_leeds_macsec_drop == setup->rule.fields.action)
        {
          rule.output_id = 0x80000000; /* IOD set to drop */
        }
        else 
        {
          rule.output_id = 0x40000000; /* IOD set to bypass */
        }
        hw_commit |= e_leeds_macsec_hw_commit_rule;
        break;

      case e_leeds_macsec_authenticate_decrypt:  

        rule.token_type  = LEEDS_MACSEC_MACSEC_TOKEN; /* MACsec enable */
        rule.pass        = 1; /* valid for ingress only, alsways set to 1 */
        rule.direction   = 1; /* ingress */
        rule.es          = 0; /* not required for ingress */
        rule.sc          = setup->rule.fields.sectag_option_sc; 
        rule.scb         = 0; /* not required for ingress */
        rule.too         = 2; /* always verify calculated authent results on ingress */

        if (30 == setup->sa_ctxt.fields.ctrl_co_offset) {
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 1; /* select 30 byte co offset */
        } else if (50 == setup->sa_ctxt.fields.ctrl_co_offset) {
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 2; /* select 50 byte co offset */
        } else if ((0 < setup->sa_ctxt.fields.ctrl_co_offset) && 
                  (128 > setup->sa_ctxt.fields.ctrl_co_offset)) {
          /* make use of the ext co offset word in token, note: we are forcing the
             header offset field to 0 
          */
          rule.eco         = 1; /* enable extended co offset */
          rule.co          = 2; /* select 50 byte co offset */
          rule.extended_co = setup->sa_ctxt.fields.ctrl_co_offset << 24;
        }
        else {
          /* no co offsets or co offset too large */
          rule.eco         = 0; /* turn off extended co offset */
          rule.co          = 0; /* no co offset */
        }
        rule.cid_update  = 1; /* always update context id internally */
        rule.oid_valid   = 0; /* the ouput identifier word is part of the token */
        rule.len_valid   = 0; /* We are always in cut-through mode, set to 0 */ 
        rule.inp_pkt_len = 0; /* always in cut-through mode, set to 0 */

        /*
        Note to remember: TCAM, Token entries are mapped 1 to 1, but not the 
        Context records. 
        We must find an available Context record, rifle thru all 16 Context records
        looking for with ToP field set to 0, don't forget to assign it to rule.context_ptr 
        and also ctxt.ctxt_id  
        Context pointer points to a valid context (range 0..16). Since context records
        are of size 0x40 words, pointer for 0th Context : 0x0 , 1st Context:0x40, 
        2nd Context : 0x80.etc 
        */

        status = leeds_macsec_ingress_find_free_ctxt_entry(port, &ctxt_entry);
        if (CS_OK != status)
        {
          /* no free entries, perhaps this is the 17th encryption flow! */
          dbg_dump(stdout, "ERROR: leeds_macsec_ingress_find_free_ctxt_entry() returned status:%d\n", status);
          return status;
        } 

        rule.context_ptr = ctxt_entry * 0x40; 
        rule.output_id   = 0;   /* ?? must configure this word */

        hw_commit |= e_leeds_macsec_hw_commit_rule;
        break;

      default:
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_setup_flow_entry(), invalid setup->rule.fields.action:%d\n", 
                 setup->rule.fields.action);
        return CS_ERROR;
        break;

    }  /* case */

    /* 
    lets setup the ingress context record if MACsec flow
    */
    switch (setup->rule.fields.action) {
      case e_leeds_macsec_drop:                 /* context record not required */
      case e_leeds_macsec_bypass:               /* context record not required */
        break;

      case e_leeds_macsec_authenticate_decrypt:  

        /* build up the control word in the context record */
        ctxt_ctrl.fields.top          = 0xf; /* must always be 0xf on ingress */
        ctxt_ctrl.fields.pack_b_op    = 0; /* used for debug, force to 0 */
        ctxt_ctrl.fields.iv03         = 0; /* IV3 field never used, force to 0 */
        ctxt_ctrl.fields.ct_len       = 0; /* used for debug, force to 0 */
        ctxt_ctrl.fields.up_seq_num   = 1; /* always update the seq number in ext memory */
        ctxt_ctrl.fields.iv_format    = 1; /* full IV mode */
        ctxt_ctrl.fields.encrypt_auth = 1; /* encrypt authent result into ICV */            
        ctxt_ctrl.fields.key          = 1; 
        ctxt_ctrl.fields.an           = setup->sa_ctxt.fields.ctrl_assoc_num; /* association num */
        ctxt_ctrl.fields.crypto_al    = 5; /* always enable AES-128 crypto algorithm */
        ctxt_ctrl.fields.digest_type  = 2; /* single authentication key */
        ctxt_ctrl.fields.authent_al   = 4; /* always enable GHASH authentication algorithm */
        ctxt_ctrl.fields.seq_type     = 1; /* 32 bit seq_num present in ctxt record */
        ctxt_ctrl.fields.ctxt_id      = 1; /* ctxt id present in ctxt record, this must enabled */ 

        if (1 == setup->rule.fields.sectag_option_es) {
          /* we will be stuffing SCI in IV0 and IV1 fields of ctxt record */
          ctxt_ctrl.fields.iv01       = 1; /* IV0 present */
          ctxt_ctrl.fields.iv02       = 1; /* IV1 present */ 
  
          /* need to confirm endianness and see page 75 of HW doc */
          ptr1 = (uint8 *)&setup->parser.fields.sci;
          ptr2 = (uint8 *)&ctxt.iv0;
          for(i=0;i<4;i++) {
            *ptr2++ = *ptr1++; /* ctxt.iv0 = sci[0..3] */
          }
          ptr2 = (uint8 *)&ctxt.iv1;
          for(i=0;i<4;i++) {
            *ptr2++ = *ptr1++; /* ctxt.iv1 = sci[4..7] */
          }
        }

        if (TRUE == setup->sa_ctxt.fields.ctrl_replay_window) {
          /* if Replay Window Feature is enabled then turn it on and stuff the mask in seq_num_mask */
          ctxt_ctrl.fields.seq_mask = 1; /* seq mask present in ctxt record */
          ctxt.seq_num_mask         = setup->sa_ctxt.fields.seq_num_mask;
    
        } else {
          ctxt_ctrl.fields.seq_mask = 0; /* seq mask not present in ctxt record */
        }

        ctxt.ctrl_word = ctxt_ctrl.regs.reg;

        ctxt.seq_num = setup->sa_ctxt.fields.seq_num; /* (packet_num) */
    
        for(i=0;i<16;i++) {
          ctxt.akey[i] = setup->sa_ctxt.fields.aes_key[i]; /* watch out for endian-ness */
          ctxt.hkey[i] = setup->sa_ctxt.fields.ghash_key[i];
        }
    
        ctxt.ctxt_id = ctxt_entry * 0x40; /* points to itself */

        hw_commit |= e_leeds_macsec_hw_commit_ctxt;
        break;

      case e_leeds_macsec_authenticate_encrypt: /* only valid on egress */
      case e_leeds_macsec_authenticate_only:    /* only valid on egress */

      default:
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_setup_flow_entry(), invalid setup->rule.fields.action:%d\n", 
                 setup->rule.fields.action);
        return CS_ERROR;
        break;

    } /* case */

    if (TRUE == setup->parser.fields.invert_mask_polar) {
      /*
      Every TCAM entry (range 0..31) has a polarity, configure MACSEC_INGRESS_TCAM_Entry_Invert_15_0 and
      MACSEC_INGRESS_TCAM_Entry_Invert_31_16
      */
    }


    /*
    Update the various options for tag parsing using MACSEC_INGRESS_TAG_CONTROL
      they are: use_inner_tag, 
                parse_802dot1q, 
                parse_802dot1s, 
                parse_QinQ      
    */

    /* 
    Specify 3 ethertypes (for the 802.1s tag frame), update MACSEC_INRESS_R802DOT1S_TAG_ET0..2
    The 3 ethertypes are pre-defined, Phil suggested we don't need an API to change them
    */

    /* if all is good, program the records to the h/w */
    if ((hw_commit & e_leeds_macsec_hw_commit_parser) && (hw_commit & e_leeds_macsec_hw_commit_rule))
    {

      status = leeds_macsec_ipr_cam_wr(port, cam_entry, &cam, &mask);
      leeds_macsec_ipr_cam_rd(port, cam_entry, &cam, &mask);

      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ipr_cam_wr() returned status:%d\n", status);
        return status;
      } 
      status = leeds_macsec_irt_wr(port, cam_entry, &rule);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_irt_wr() returned status:%d\n", status);
        return status;
      } 

      /* context record updates are optional */
      if (hw_commit & e_leeds_macsec_hw_commit_ctxt)
      {
        status = leeds_macsec_ict_wr(port, ctxt_entry, &ctxt);
        if (CS_OK != status)
        {
          dbg_dump(stdout, "ERROR: leeds_macsec_ict_wr() returned status:%d\n", status);
          return status;
        } 
        /*
        Update table to map ctxt index to SA's for stats purposes
        */
        status = leeds_macsec_ingress_update_sa_map(port, cam_entry, ctxt_entry, TRUE);
        if (CS_OK != status)
        {
          dbg_dump(stdout, "ERROR: leeds_macsec_ingress_update_sa_map() returned status:%d\n", status);
          return status;
        } 
      }

      /* The last step is to enable the TCAM entry valid bit */
      status = leeds_macsec_ingress_update_cam_entry_valid(port, cam_entry, TRUE);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_update_cam_entry_valid() returned status:%d\n", status);
        return status;
      } 
    }
    return CS_OK;

} /* leeds_macsec_ingress_setup_flow_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to write a 32 bit register to the MACsec block. MACsec 32 bit register
 * addresses point to the MS 16 bits of a 32 bit register thus the MS 16 bits is written to
 * address+0, the LS 16 bits written to address+1.
 * Note: Currently not used.
 *
 *  @param port        [I]  -  The port number of the device to access.
 *  @param addr        [I]  -  Identifies the address where the data is to be written to.
 *  @param data        [I]  -  contains the 32 bit data
 *
 *  @return                 -  CS_OK or CS_ERROR
 *  @private
 *
 */
cs_status leeds_macsec_32bit_reg_set(uint32 port, uint16 addr, uint32 data)
{
    cs_status                status;
    leeds_macsec_32bit_reg_t reg;
    
    reg.uint32_reg.reg = data;

    status = leeds_reg_set(port, addr,   reg.uint16_reg.reg[1]);
    status = leeds_reg_set(port, addr+1, reg.uint16_reg.reg[0]);

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to set the default token rules for different frame types
 * to strict or non-strict frame validation modes.
 *
 *  @param port        [I]  -  The port number of the device to access.
 *  @param frame_type  [I]  -  Identifies the frames type, one of: 
 *                               e_leeds_macsec_ingress_controlled,
 *                               e_leeds_macsec_ingress_un_controlled,
 *                               e_leeds_macsec_ingress_invalid_frame,
 *                               e_leeds_macsec_egress_security_miss
 *  @param mode        [I]  -  The mode, one of: 
                                 e_leeds_macsec_strict, 
                                 e_leeds_macsec_non_strict 
 *
 *  @return                 -  CS_OK or CS_ERROR
 *
 */

cs_status leeds_macsec_frame_validation_mode(uint32 port,
                                             e_leeds_macsec_frame_type frame_type, 
                                             e_leeds_macsec_mode mode)
{
    /* 
    In strict mode we shall configure a bypass token with the Drop bit set in
    the Output Identifier, this will result in a corrupt frame that will then be
    dropped up-stream. This is so we can have stats measure dropped frames 
    (ie no silent discards)
    */

    cs_status                   status;
    leeds_macsec_frame_valid_token_rec_t token;

    memset(&token, 0, sizeof(token));

    token.control_word = 0x82040000; /* configure a special bypass token */ 
    token.ctxt_id      = 0;          /* context pointer is 0 */

    switch (mode) 
    {
      case e_leeds_macsec_strict:
        /* config Output Identifier to drop */
        token.output_id = 0x80000000; /* IOD set to drop */
        break;

      case e_leeds_macsec_non_strict:
        /* config Output Identifier to bypass */
        token.output_id = 0x40000000; /* IOD set to bypass */
        break;

      default:
        /* invalid mode */
        dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode(), mode:%d\n", mode);
        return CS_ERROR;
        break;
    }

    token.frame_type = frame_type;
    switch (frame_type) 
    {
      case e_leeds_macsec_ingress_controlled:
      case e_leeds_macsec_ingress_un_controlled:
      case e_leeds_macsec_ingress_invalid_frame:
      case e_leeds_macsec_egress_security_miss:
        /* update the HW */
        status = leeds_macsec_iefv_tok_wr(0, &token);
        if (CS_OK != status)
        {
            dbg_dump(stdout, "ERROR: blabla...\n");
        }
        break;

      default:
        /* invalid frame type */
        dbg_dump(stdout, "ERROR: leeds_macsec_frame_validation_mode(), frame_type:%d\n", frame_type);
        return CS_ERROR;
        break;
    }

    return CS_OK;

} /* leeds_macsec_frame_validation_mode */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to set the default action for Consistency Check events.
 *
 *  @param port           [I]  - The port number of the device to access.
 *  @param cc_entry       [I]  - The entry index within the Consistency Check to program (range 0-15).
 *  @param cc_event       [I]  - Consistency Check event, one of: 
 *                                 cc_miss (the frame hit no rule) or 
 *                                 cc_hit (he frame hit a rule).
 *  @param cc_frame_type  [I]  - Consistency Check frame type, one of:
 *                                 cc_control (frame is of type control-plane) or 
 *                                 cc_non_control (frame is of type data-plane).
 *  @param cc_action      [I]  - Consistency Check action, one of:
 *                                 cc_drop (frame is to be dropped) or
 *                                 cc_bypass (frame is to bypassed).
 *
 *  @return                    -  CS_OK or CS_ERROR
 *
 */

cs_status leeds_macsec_ingress_cc_default_action(uint32 port,
  uint32                       cc_entry,
  e_leeds_macsec_cc_event      cc_event, 
  e_leeds_macsec_cc_frame_type cc_frame_type, 
  e_leeds_macsec_cc_action     cc_action)
{

    uint16    reg_data;
    cs_status status = FALSE;
 
    if (e_leeds_macsec_cc_miss == cc_event)
    {
      status |= leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_MISS_ACTION, &reg_data);
      if (e_leeds_macsec_cc_non_control == cc_frame_type)
      {
        if (e_leeds_macsec_cc_drop == cc_action)
        {
          reg_data &= ~0x01;
        }
        else
        {
          reg_data |= 0x01;
        }
      }
      else if (e_leeds_macsec_cc_control == cc_frame_type) /* control frames */
      {
        if (e_leeds_macsec_cc_drop == cc_action)
        {
          reg_data &= ~0x02;
        }
        else
        {
          reg_data |= 0x02;
        }
      }
      else
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action(), cc_frame_type:%d\n", cc_frame_type);
        return CS_ERROR;

      }
      status |= leeds_reg_set(port, LEEDS_MACSEC_INGRESS_CCTCAM_MISS_ACTION, reg_data);
    }
    else if (e_leeds_macsec_cc_hit == cc_event) /* hit event */
    {
      if (e_leeds_macsec_cc_non_control == cc_frame_type)
      {
        status |= leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_NON_CONTROL_FRAME, &reg_data);
        if (e_leeds_macsec_cc_drop == cc_action)
        {
          reg_data &= ~(1 << cc_entry);
        }
        else
        {
          reg_data |= (1 << cc_entry);
        }
        status |= leeds_reg_set(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_NON_CONTROL_FRAME, reg_data);
      }
      else if (e_leeds_macsec_cc_control == cc_frame_type) /* control frames */
      {
        status |= leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_CONTROL_FRAME, &reg_data);
        if (e_leeds_macsec_cc_drop == cc_action)
        {
          reg_data &= ~(1 << cc_entry);
        }
        else
        {
          reg_data |= (1 << cc_entry);
        }
        status |= leeds_reg_set(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_CONTROL_FRAME, reg_data);
      }
      else
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action(), cc_frame_type:%d\n", cc_frame_type);
        return CS_ERROR;

      }
    }
    else
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_cc_default_action(), cc_event:%d\n", cc_event);
      return CS_ERROR;
    }

    return status;

} /* leeds_macsec_ingress_cc_default_action */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find a free ingress Context record entry. A free entry
 * is found by rifling thru all 16 Context records looking for an unused one. An
 * unused Context record is one whose ToP (type of Packet) field is set to 0.
 * If a free entry is found, the entry number is copied to the entry argument and
 * the method returns CS_OK otherwise, if no free entries are found, the method 
 * returns CS_ERROR. 
 *
 *  @param port        [I] -  The port to access. 
 *  @param ctxt_entry  [O] -  The free Context record entry (0..15). 
 *
 *  @return                -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_find_free_ctxt_entry(uint32 port,
                                                    uint16 *ctxt_entry)
{
    cs_status                status;
    leeds_macsec_ctxt_rec_t  ctxt;
    uint8                    entry_index;
    uint8                    found = FALSE;
    leeds_macsec_ctxt_ctrl_t ctxt_ctrl;

 
    /* lets rifle thru all 16 Context records */
    for (entry_index=0; entry_index<16; entry_index++)
    {
      status = leeds_macsec_ict_rd(port, entry_index, &ctxt);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ict_rd() returned status:%d\n", status);
        return status;
      }
 
      ctxt_ctrl.regs.reg = ctxt.ctrl_word;

      if (0 == ctxt_ctrl.fields.top) 
      {
        *ctxt_entry = entry_index;
        found = TRUE;
        break;
      }
    }
               
    if (TRUE == found)
    { 
      return CS_OK;
    }
    return CS_ERROR;

} /* leeds_macsec_ingress_find_free_ctxt_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find a free ingress Context record entry. A free entry
 * is found by rifling thru all 16 Context records looking for an unused one. An
 * unused Context record is one whose ToP (type of Packet) field is set to 0.
 * If a free entry is found, the entry number is copied to the entry argument and
 * the method returns CS_OK otherwise, if no free entries are found, the method 
 * returns CS_ERROR. 
 *   
 *  @param port        [I] -  The port to access.
 *  @param ctxt_entry  [O] -  The free Context record entry (0..15). 
 *
 *  @return                -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_egress_find_free_ctxt_entry(uint32 port,
                                                   uint16 *ctxt_entry)
{

    cs_status                status;
    leeds_macsec_ctxt_rec_t  ctxt;
    uint8                    entry_index;
    uint8                    found = FALSE;
    leeds_macsec_ctxt_ctrl_t ctxt_ctrl;
 
    /* lets rifle thru all 16 Context records */
    for (entry_index=0; entry_index<16; entry_index++)
    {
      status = leeds_macsec_ect_rd(port, entry_index, &ctxt);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ect_rd() returned status:%d\n", status);
        return status;
      }
 
      ctxt_ctrl.regs.reg = ctxt.ctrl_word;

      if (0 == ctxt_ctrl.fields.top) 
      {
        *ctxt_entry = entry_index;
        found = TRUE;
        break;
      }
    }
               
    if (TRUE == found)
    { 
      return CS_OK;
    }
    return CS_ERROR;


} /* leeds_macsec_egress_find_free_ctxt_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to delete an ingress Context record entry. To delete
 * an entry, the ToP (type of Packet) field is set to 0.
 *
 *  @param port        [I] -  The port to access. 
 *  @param ctxt_entry  [I] -  The Context record entry to delete (0..15).
 *
 *  @return                -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_delete_ctxt_entry(uint32 port,
                                                 uint16 cam_entry,
                                                 uint16 ctxt_entry)
{
    cs_status                status;
    leeds_macsec_ctxt_rec_t  ctxt;
    leeds_macsec_ctxt_ctrl_t ctxt_ctrl;
 
    status = leeds_macsec_ict_rd(port, ctxt_entry, &ctxt);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ict_rd() returned status:%d\n", status);
      return status;
    }
 
    ctxt_ctrl.regs.reg = ctxt.ctrl_word;

    if (0x0f != ctxt_ctrl.fields.top)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_delete_ctxt_entry() type_of_packet != 0xff:%d\n", 
               ctxt_ctrl.fields.top);
      return CS_ERROR;
    }

    ctxt_ctrl.fields.top = 0;
    ctxt.ctrl_word = ctxt_ctrl.regs.reg;

    status = leeds_macsec_ict_wr(port, ctxt_entry, &ctxt);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ict_wr() returned status:%d\n", status);
      return status;
    }
 
    /*
    Update table to no longer map ctxt index to SA's for stats purposes
    */
    status = leeds_macsec_ingress_update_sa_map(port, cam_entry, ctxt_entry, FALSE);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_update_sa_map() returned status:%d\n", status);
      return status;
    } 

    return CS_OK;

} /* leeds_macsec_ingress_delete_ctxt_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to delete an egress Context record entry. To delete
 * an entry, the ToP (type of Packet) field is set to 0.
 *
 *  @param port        [I] -  The port to access. 
 *  @param ctxt_entry  [I] -  The Context record entry to delete (0..15). 
 *
 *  @return                -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_egress_delete_ctxt_entry(uint32 port,
                                                uint16 cam_entry,
                                                uint16 ctxt_entry)
{

    cs_status                 status;
    leeds_macsec_ctxt_rec_t   ctxt;
    leeds_macsec_ctxt_ctrl_t  ctxt_ctrl;
 
    status = leeds_macsec_ect_rd(port, ctxt_entry, &ctxt);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ect_rd() returned status:%d\n", status);
      return status;
    }

    ctxt_ctrl.regs.reg = ctxt.ctrl_word;

    if (0x06 != ctxt_ctrl.fields.top)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_egress_delete_ctxt_entry() type_of_packet != 0x06:%d\n", 
               ctxt_ctrl.fields.top);
      return CS_ERROR;
    }
 
    ctxt_ctrl.fields.top = 0;
    ctxt.ctrl_word = ctxt_ctrl.regs.reg;

    status = leeds_macsec_ect_wr(port, ctxt_entry, &ctxt);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ect_wr() returned status:%d\n", status);
      return status;
    }

    /*
    Update table to no longer map ctxt index to SA's for stats purposes
    */
    status = leeds_macsec_egress_update_sa_map(port, cam_entry, ctxt_entry, FALSE);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_egress_update_sa_map() returned status:%d\n", status);
      return status;
    } 

    return CS_OK;


} /* leeds_macsec_egress_delete_ctxt_entry */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find a free ingress Consistency Check record entry. 
 * A free entry is found by reading the CC_TCAM_Entry_Valid register where each bit 
 * corresponds to a CC entry. An unused Consistency Check entry is one whose bit 
 * is set to 0. If a free entry is found, the entry number is copied to the entry 
 * argument and the method returns CS_OK otherwise, if no free entries are found, 
 * the method returns CS_ERROR. 
 *
 *  @param port      [I] -  The port to access.
 *  @param cc_entry  [O] -  The free Consistency Check record entry (0..15). 
 *
 *  @return              -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_find_free_cc_entry(uint32 port,
                                                  uint16 *cc_entry)
{
    cs_status               status;
    uint8                   entry_index;
    uint16                  reg_data, bit_match;
    uint8                   found = FALSE;
 
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Valid, &reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
      return status;
    }
 
    /* if there is at least one free CC entry */
    if (0xffff != reg_data) 
    {
      /* lets find the first one */
      for (entry_index=0; entry_index<16; entry_index++)
      {
        bit_match = 1<<entry_index;
        if ((bit_match & ~reg_data) == bit_match)
        {   
          *cc_entry = entry_index;
          found = TRUE;
          break;
        }
      }
    }
               
    if (TRUE == found)
    { 
      return CS_OK;
    }
    return CS_ERROR;

} /* leeds_macsec_ingress_find_free_cc_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to delete an ingress Consistency Check record entry. 
 * A entry is deleted by writing to the CC_TCAM_Entry_Valid register where each bit 
 * corresponds to a CC entry. An enabled Consistency Check record is one whose bit 
 * is set to 1. To delete the entry, a 0 is written to that bit location. 
 *
 *  @param port      [I] -  The port to access. 
 *  @param cc_entry  [I] -  The free Consistency Check record entry (0..15). 
 *
 *  @return              -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_delete_cc_entry(uint32 port,
                                               uint16 cc_entry)
{
    cs_status               status;
    uint16                  reg_data;
 
    if (cc_entry >= 16) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_delete_cc_entry(), cc_entry >= 16, cc_entry:%d\n", cc_entry);
      return CS_BOUNDS;
    }
 
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Valid, &reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
      return status;
    }
 
    /* clear the CC entry bit position in the bit map */ 
    reg_data &= ~(1 << cc_entry);
 
    status = leeds_reg_set(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Valid, reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_set() returned status:%d\n", status);
      return status;
    }
 
    return CS_OK;

} /* leeds_macsec_ingress_delete_cc_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 * This method is called to configure an ingress Consistency Check entry by writing to the 
 * CC TCAM registers. Prior to calling the method, an unused (free) Consistency Check
 * entry must be found by calling method leeds_macsec_ingress_find_free_cc_entry().
 *
 *  @param port      [I] -  The port to access.
 *  @param cc_entry  [I] -  The CC TCAM entry within the table to access.
 *  @param setup     [I] -  The configuration info to program the CC.
 *
 *  @return                    -  CS_OK or CS_ERROR
 *
 */
cs_status leeds_macsec_ingress_update_cc_entry(
  uint32                          port,
  uint32                          cc_entry,
  leeds_macsec_ingress_setup_cc_t *setup)

{

    leeds_macsec_chk_cam_mask_t  cmask;
    leeds_macsec_chk_cam_entry_t ccam;
    cs_status                    status;
    uint16                       invert_bits;
 
    ccam.et    = setup->fields.cc_etype_exp;
    ccam.ev    = setup->fields.cc_etype_gt_flag;
    ccam.tg    = setup->fields.cc_vlan_tag;
    ccam.vlan  = setup->fields.cc_vlan;
    ccam.sh    = setup->fields.cc_dec_hit_flag;
    ccam.sai   = setup->fields.cc_dec_hit_idx;
    
    cmask.et   = (setup->fields.cc_mask & e_leeds_macsec_cc_etype_field_mask)        ? TRUE : FALSE;
    cmask.ev   = (setup->fields.cc_mask & e_leeds_macsec_cc_etype_v_field_mask)      ? TRUE : FALSE;
    cmask.tg   = (setup->fields.cc_mask & e_leeds_macsec_cc_vlan_tg_field_mask)      ? TRUE : FALSE;
    cmask.vlan = (setup->fields.cc_mask & e_leeds_macsec_cc_vlan_field_mask)         ? TRUE : FALSE;
    cmask.sh   = (setup->fields.cc_mask & e_leeds_macsec_cc_dec_hit_flag_field_mask) ? TRUE : FALSE;
    cmask.sai  = (setup->fields.cc_mask & e_leeds_macsec_cc_dec_hit_idx_field_mask)  ? TRUE : FALSE;

    /* note that the following method hits the TCAM_Entry_valid register */ 
    status = leeds_macsec_chk_cam_wr(port, cc_entry, &ccam, &cmask);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_chk_cam_wr() returned status:%d\n", status);
      return status;
    }

    leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Invert, &invert_bits);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
      return status;
    }

    if (setup->fields.cc_invert_mask_polar)
    {
      invert_bits |= (1 << cc_entry);
    }
    else 
    {
      invert_bits &= ~(1 << cc_entry);
    }

    leeds_reg_set(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Invert, invert_bits);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_set() returned status:%d\n", status);
      return status;
    }
 
    return CS_OK;

} /* leeds_macsec_ingress_update_cc_entry */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to enable a TCAM egress entry by writing to the TCAM 
 * Entry Valid register.
 *
 *  @param port       [I] -  The port to access. 
 *  @param cam_entry  [I] -  The TCAM entry within the table to access. 
 *  @param flag       [I] -  True/False where True=enable, False=disable.
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */
cs_status leeds_macsec_egress_update_cam_entry_valid(
  uint32                    port,
  uint32                    cam_entry,
  uint32                    flag)
{
    cs_status status;
    uint32    addr;
    uint16    reg_data;
 
      
    if(15 >= cam_entry)
    {
      addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_15_0;
    }
    else if (31 >= cam_entry) 
    {
      addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_31_16;
    } 
    else 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_egress_update_cam_entry_valid(), cc_entry > 31, cam_entry:%d\n", cam_entry);
      return CS_BOUNDS;
    }
 
    status =leeds_reg_get(port, addr, &reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_set() returned status:%d\n", status);
      return status;
    }
 
    if (TRUE == flag)
    {
      /* set the bit position entry in the bit map */ 
      reg_data |= (0x01 << cam_entry);
    }
    else
    {
      /* clear the bit position entry in the bit map */ 
      reg_data &= ~(0x01 << cam_entry);
    }
 
    status = leeds_reg_set(port, addr, reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_set() returned status:%d\n", status);
      return status;
    }

    return CS_OK;

} /* leeds_macsec_egress_update_cam_entry_valid */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to enable a TCAM ingress entry by writing to the TCAM 
 * Entry Valid register.
 *
 *  @param port       [I] -  The port to access. 
 *  @param cam_entry  [I] -  The TCAM entry within the table to access. 
 *  @param flag       [I] -  True/False where True=enable, False=disable.
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */
cs_status leeds_macsec_ingress_update_cam_entry_valid(
  uint32                    port,
  uint32                    cam_entry,
  uint32                    flag)
{
    cs_status status;
    uint32    addr;
    uint16    reg_data;
 
      
    if(15 >= cam_entry)
    {
      addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_15_0;
    }
    else if (31 >= cam_entry) 
    {
      addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_31_16;
    } 
    else 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_update_cam_entry_valid(), cc_entry > 31, cam_entry:%d\n", cam_entry);
      return CS_BOUNDS;
    }
 
    status = leeds_reg_get(port, addr, &reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
      return status;
    }
 
    if (TRUE == flag)
    {
      /* set the bit position entry in the bit map */ 
      reg_data |= (1 << (cam_entry & 0xf));
    }
    else
    {
      /* clear the bit position entry in the bit map */ 
      reg_data &= ~(1 << (cam_entry & 0xf));
    }
 
    status = leeds_reg_set(port, addr, reg_data);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_reg_set() returned status:%d\n", status);
      return status;
    }

    return CS_OK;

} /* leeds_macsec_ingress_update_cam_entry_valid */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find an ingress TCAM entry whose SCI and TCI maches the ones 
 * provided in the arguments. If a matching TCAM entry is found, the entry number is 
 * copied to the entry argument and the method returns CS_OK otherwise, if no matching 
 * TCAM entries are found, the method returns CS_ERROR. 
 *
 * Note:  On ingress, the SCI and TCI arguments are matched to the parser TCAM record sci and tci_an
 * fields. They contain the 8 byte SCI value. 
 *
 *  @param port       [I] -  The port to access.
 *  @param sci        [I] -  The SCI to match.
 *  @param tci        [I] -  The TCI to match.
 *  @param cam_entry  [O] -  The matching TCAM entry (0..31). 
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_find_cam_entry(uint32  port,
  uint64  sci,
  uint8   tci,
  uint16* cam_entry)
{
    cs_status                    status;
    leeds_macsec_ipr_cam_entry_t cam;
    leeds_macsec_ipr_cam_mask_t  mask;
    uint8                        entry_index;
    uint8                        reg_index;
    uint32                       addr;
    uint16                       reg_data;
    uint8                        found = FALSE;
 
    for (reg_index=0; (reg_index<2 && FALSE==found); reg_index++) 
    {
      if (0 == reg_index) 
      {
        addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_15_0;
      }
      else
      {
        addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_31_16;
      }
 
      status = leeds_reg_get(port, addr, &reg_data);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
        return status;
      }
 
      /* if there is at least one active entry */
      if (0 != reg_data)
      {
        /* lets find it */
        for (entry_index=0; entry_index<16; entry_index++)
        {
          if ((1<<entry_index) & reg_data)
          {
            /* now lets match it's TCI and SCI */
            *cam_entry = entry_index + (reg_index*16);

            leeds_macsec_ipr_cam_rd(port, *cam_entry, &cam, &mask);
            if (CS_OK != status) 
            {
              dbg_dump(stdout, "ERROR: leeds_macsec_ipr_cam_rd() returned status:%d\n", status);
              return status;
            }

            if ((cam.sci == sci) && (cam.tci_an == tci))
            {
              found = TRUE;
              break;
            }
          }
        }
      }
               
      if (TRUE == found)
      { 
        return CS_OK;
      }
    }
    return CS_ERROR;

} /* leeds_macsec_ingress_find_cam_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find an egress TCAM entry whose SCI and TCI maches the ones 
 * provided in the arguments. If a matching TCAM entry is found, the entry number is 
 * copied to the entry argument and the method returns CS_OK otherwise, if no matching 
 * TCAM entries are found, the method returns CS_ERROR. 
 * 
 * Note: On egress, the SCI and TCI arguments are matched to the Context record IV0 and IV1
 * fields. They contain the 8 byte SCI value. 
 *
 *  @param port       [I] -  The port to access. 
 *  @param sci        [I] -  The SCI to match.
 *  @param tci        [I] -  The TCI to match.
 *  @param cam_entry  [O] -  The matching TCAM entry (0..31). 
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_egress_find_cam_entry(uint32  port,
  uint64  sci,
  uint8   tci,
  uint16* cam_entry)
{
    cs_status                    status;
    uint8                        entry_index;
    uint8                        reg_index;
    uint8                        ctxt_entry;
    uint32                       addr;
    uint16                       reg_data;
    uint8                        found = FALSE;
    uint64                       sci_to_match;
    leeds_macsec_token_t         rule; 
    leeds_macsec_ctxt_rec_t      ctxt;
 
    
    for (reg_index=0; (reg_index<2 && FALSE==found); reg_index++) 
    {
      if (0 == reg_index) 
      {
        addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_15_0;
      }
      else
      {
        addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_31_16;
      }
 
      status = leeds_reg_get(port, addr, &reg_data);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
        return status;
      }
 
      /* if there is at least one active entry */
      if (0 != reg_data)
      {
        /* lets find it */
        for (entry_index=0; entry_index<16; entry_index++)
        {
          if ((1<<entry_index) & reg_data)
          {
            /* get the Token rule entry */
            status = leeds_macsec_ert_rd(port,  
                                         entry_index+(reg_index*16), 
                                         &rule);

            if (CS_OK != status) 
            {
              dbg_dump(stdout, "ERROR: leeds_macsec_irt_rd() returned status:%d\n", status);
              return status;
            }
            /* only the MACsec flows have TCI and SCI defined */
            if (LEEDS_MACSEC_MACSEC_TOKEN == rule.token_type)
            {
              ctxt_entry = rule.context_ptr / 0x40;
           
              if (15 < ctxt_entry) 
              {
                /* funny, this MACsec entry should point to a Context record */
                continue;
              }
              /* now lets read the Context record */
              status = leeds_macsec_ect_rd(port, 
                                           ctxt_entry,
                                           &ctxt);
              if (CS_OK != status) 
              {
                dbg_dump(stdout, "ERROR: leeds_macsec_ect_rd() returned status:%d\n", status);
                return status;
              }

              sci_to_match =  ctxt.iv1;
              sci_to_match <<= 32;
              sci_to_match |= ctxt.iv0;
              /* now lets match it's TCI and SCI */
              if (sci_to_match == sci) 
              {
                *cam_entry = entry_index + (reg_index*16);
                found = TRUE;
                break;
              }
            }
          }
        }
      }
               
      if (TRUE == found)
      { 
        return CS_OK;
      }
    }
    return CS_ERROR;


} /* leeds_macsec_egress_find_cam_entry */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find a free ingress TCAM entry. A free entry is found by reading the 
 * TCAM_Entry_Valid registers where each bit corresponds to a TCAM entry. An unused TCAM entry is 
 * one whose bit is set to 0. If a free entry is found, the entry number is copied to the entry 
 * argument and the method returns CS_OK otherwise, if no free TCAM entries are found, the method 
 * returns CS_ERROR. 
 *
 *  @param port       [I] -  The port to access.
 *  @param cam_entry  [O] -  The free TCAM entry (0..31).
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_find_free_cam_entry(uint32 port,
                                               uint16 *cam_entry)
{
    cs_status status;
    uint8     entry_index;
    uint8     reg_index;
    uint32    addr;
    uint16    reg_data,  bit_match;
    uint8     found = FALSE;
 
    for (reg_index=0; (reg_index<2 && FALSE==found); reg_index++) 
    {
      if (0 == reg_index) 
      {
        addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_15_0;
      }
      else
      {
        addr = LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_31_16;
      }
 
      status = leeds_reg_get(port, addr, &reg_data);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
        return status;
      }
 
      /* if there is at least one free entry */
      if (0xff != reg_data)
      {
        /* lets find it */
        for (entry_index=0; entry_index<16; entry_index++)
        {
          bit_match = 1<<entry_index;
          if ((bit_match & ~reg_data) == bit_match) 
          {
            *cam_entry = entry_index + (reg_index*16);
            found = TRUE;
            break;
          }
        }
      }
               
      if (TRUE == found)
      { 
        return CS_OK;
      }
    }
    return CS_ERROR;

} /* leeds_macsec_ingress_find_free_cam_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to find a free egress TCAM entry. The free entry
 * is found by reading the Entry Valid register. If a free entry is found, 
 * the entry number is copied to the entry argument and the method returns
 * CS_OK otherwise, if no free TCAM entries are found, the method returns CS_ERROR. 
 *   
 *  @param port       [I] -  The port to access. 
 *  @param cam_entry  [O] -  The free TCAM entry (0..31). 
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_egress_find_free_cam_entry(uint32 port,
                                                  uint16 *cam_entry)
{

    cs_status status;
    uint8     entry_index;
    uint8     reg_index;
    uint32    addr;
    uint16    reg_data,  bit_match;
    uint8     found = FALSE;
 
    for (reg_index=0; (reg_index<2 && FALSE==found); reg_index++) 
    {
      if (0 == reg_index) 
      {
        addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_15_0;
      }
      else
      {
        addr = LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_31_16;
      }
 
      status = leeds_reg_get(port, addr, &reg_data);
      if (CS_OK != status) 
      {
        dbg_dump(stdout, "ERROR: leeds_reg_get() returned status:%d\n", status);
        return status;
      }
 
      /* if there is at least one free entry */
      if (0xff != reg_data)
      {
        /* lets find it */
        for (entry_index=0; entry_index<16; entry_index++)
        {
          bit_match = 1<<entry_index;
          if ((bit_match & ~reg_data) == bit_match) 
          {
            *cam_entry = entry_index + (reg_index*16);
            found = TRUE;
            break;
          }
        }
      }
               
      if (TRUE == found)
      { 
        return CS_OK;
      }
    }
    return CS_ERROR;

} /* leeds_macsec_egress_find_free_cam_entry */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to disable an egress TCAM entry. If the TCAM entry was configured for
 * a MACsec flow, it's associated Context record is disabled also.
 *
 *  @param port       [I] -  The port to access. 
 *  @param cam_entry  [I] -  The TCAM entry to invalidate.
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_egress_delete_cam_entry(uint32 port, uint32 cam_entry)
{

    cs_status               status;
    leeds_macsec_token_t    rule; 
    uint32                  ctxt_entry;
 
    /* Update the egress entry valid TCAM entry to mark it as invalid */
    status = leeds_macsec_egress_update_cam_entry_valid(port, cam_entry, FALSE);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_egress_update_cam_entry_valid() returned status:%d\n", status);
      return status;
    }
 
    /* if the TCAM entry has a corresponding Context entry then release the Context entry */
 
    /* get the Token rule entry */
    status = leeds_macsec_ert_rd(port,  
                                 cam_entry, 
                                 &rule);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ert_rd() returned status:%d\n", status);
      return status;
    }
 
    /* if it has an associated Context record */
    if (LEEDS_MACSEC_MACSEC_TOKEN == rule.token_type)
    {
      ctxt_entry = rule.context_ptr / 0x40;
    
      if (15 < ctxt_entry) 
      {
        /* Context entry number out of range */
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_delete_cam_entry(), ctxt_entry out of range:%d\n", ctxt_entry);
        return CS_ERROR;
      }
    
      /* now lets free up the Context record */
      status = leeds_macsec_egress_delete_ctxt_entry(port, cam_entry, ctxt_entry);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_egress_delete_ctxt_entry() returned status:%d\n", status);
        return status;
      }
 
    }
    return CS_OK;

} /* leeds_macsec_egress_delete_cam_entry */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to disable an ingress TCAM entry. If the TCAM entry was configured for
 * a MACsec flow, it's associated Context record is disabled also.
 *
 *  @param port       [I] -  The port to access. 
 *  @param cam_entry  [I] -  The TCAM entry to invalidate.
 *
 *  @return               -  CS_OK or CS_ERROR.
 *
 */

cs_status leeds_macsec_ingress_delete_cam_entry(uint32 port, uint32 cam_entry)
{

    cs_status               status;
    leeds_macsec_token_t    rule; 
    uint32                  ctxt_entry;
 
    /* Update the ingress entry valid TCAM entry to mark it as invalid */
    status = leeds_macsec_ingress_update_cam_entry_valid(port, cam_entry, FALSE);
    if (CS_OK != status)
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_ingress_update_cam_entry_valid() returned status:%d\n", status);
      return status;
    }
 
    /* if the TCAM entry has a corresponding Context entry then release the Context entry */
 
    /* get the Token rule entry */
    status = leeds_macsec_irt_rd(port,  
                                 cam_entry, 
                                 &rule);
    if (CS_OK != status) 
    {
      dbg_dump(stdout, "ERROR: leeds_macsec_irt_rd() returned status:%d\n", status);
      return status;
    }
 
    /* if it has an associated Context record */
    if (LEEDS_MACSEC_MACSEC_TOKEN == rule.token_type)
    {
      ctxt_entry = rule.context_ptr / 0x40;
    
      if (15 < ctxt_entry) 
      {
        /* Context entry number out of range */
        return CS_ERROR;
      }
    
      /* now lets free up the Context record */
      status = leeds_macsec_ingress_delete_ctxt_entry(port, cam_entry, ctxt_entry);
      if (CS_OK != status)
      {
        dbg_dump(stdout, "ERROR: leeds_macsec_ingress_delete_ctxt_entry() returned status:%d\n", status);
        return status;
      }
 
    }
    return CS_OK;

} /* leeds_macsec_ingress_delete_cam_entry */


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to update the TCAM entry to the ingress Security Association Map.
 *
 *  @param port       [I] -  The port number of the device to access. 
 *  @param cam_entry  [I] -  The CAM entry number
 *  @param ctxt_entry [I] -  The Context entry number (same as SA)
 *  @param enable     [I] -  Enable the entry flag, TRUE or FALSE
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_ingress_update_sa_map(
    uint32  port,
    uint32  cam_entry,
    uint32  ctxt_entry,
    uint8   enable)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    
    leeds_macsec_sa_map_pkd_t sam_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress Security Association Map\n");
#endif

    memset(sam_pkd.bytes.bytes, 0, sizeof(sam_pkd));
   
    addr = LEEDS_MACSEC_INGRESS_STCAM_SA_MAP9;

    for(i = 0; i < sizeof(sam_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        sam_pkd.regs.regs[i] = ntohs(reg_data);
    }

    /* Set the field in the SAM record */
    if (TRUE == enable)
    {
      reg_data = ctxt_entry | 0x10;
    }
    else
    {
      reg_data = 0;
    }

    switch (cam_entry)
    {
        case 0 : SET_MSEC_SA_MAP_TCAM_00(sam_pkd.bytes.bytes, reg_data); break;
        case 1 : SET_MSEC_SA_MAP_TCAM_01(sam_pkd.bytes.bytes, reg_data); break;
        case 2 : SET_MSEC_SA_MAP_TCAM_02(sam_pkd.bytes.bytes, reg_data); break;
        case 3 : SET_MSEC_SA_MAP_TCAM_03(sam_pkd.bytes.bytes, reg_data); break;
        case 4 : SET_MSEC_SA_MAP_TCAM_04(sam_pkd.bytes.bytes, reg_data); break;
        case 5 : SET_MSEC_SA_MAP_TCAM_05(sam_pkd.bytes.bytes, reg_data); break;
        case 6 : SET_MSEC_SA_MAP_TCAM_06(sam_pkd.bytes.bytes, reg_data); break;
        case 7 : SET_MSEC_SA_MAP_TCAM_07(sam_pkd.bytes.bytes, reg_data); break;
        case 8 : SET_MSEC_SA_MAP_TCAM_08(sam_pkd.bytes.bytes, reg_data); break;
        case 9 : SET_MSEC_SA_MAP_TCAM_09(sam_pkd.bytes.bytes, reg_data); break;
        case 10: SET_MSEC_SA_MAP_TCAM_10(sam_pkd.bytes.bytes, reg_data); break;
        case 11: SET_MSEC_SA_MAP_TCAM_11(sam_pkd.bytes.bytes, reg_data); break;
        case 12: SET_MSEC_SA_MAP_TCAM_12(sam_pkd.bytes.bytes, reg_data); break;
        case 13: SET_MSEC_SA_MAP_TCAM_13(sam_pkd.bytes.bytes, reg_data); break;
        case 14: SET_MSEC_SA_MAP_TCAM_14(sam_pkd.bytes.bytes, reg_data); break;
        case 15: SET_MSEC_SA_MAP_TCAM_15(sam_pkd.bytes.bytes, reg_data); break;
        case 16: SET_MSEC_SA_MAP_TCAM_16(sam_pkd.bytes.bytes, reg_data); break;
        case 17: SET_MSEC_SA_MAP_TCAM_17(sam_pkd.bytes.bytes, reg_data); break;
        case 18: SET_MSEC_SA_MAP_TCAM_18(sam_pkd.bytes.bytes, reg_data); break;
        case 19: SET_MSEC_SA_MAP_TCAM_19(sam_pkd.bytes.bytes, reg_data); break;
        case 20: SET_MSEC_SA_MAP_TCAM_20(sam_pkd.bytes.bytes, reg_data); break;
        case 21: SET_MSEC_SA_MAP_TCAM_21(sam_pkd.bytes.bytes, reg_data); break;
        case 22: SET_MSEC_SA_MAP_TCAM_22(sam_pkd.bytes.bytes, reg_data); break;
        case 23: SET_MSEC_SA_MAP_TCAM_23(sam_pkd.bytes.bytes, reg_data); break;
        case 24: SET_MSEC_SA_MAP_TCAM_24(sam_pkd.bytes.bytes, reg_data); break;
        case 25: SET_MSEC_SA_MAP_TCAM_25(sam_pkd.bytes.bytes, reg_data); break;
        case 26: SET_MSEC_SA_MAP_TCAM_26(sam_pkd.bytes.bytes, reg_data); break;
        case 27: SET_MSEC_SA_MAP_TCAM_27(sam_pkd.bytes.bytes, reg_data); break;
        case 28: SET_MSEC_SA_MAP_TCAM_28(sam_pkd.bytes.bytes, reg_data); break;
        case 29: SET_MSEC_SA_MAP_TCAM_29(sam_pkd.bytes.bytes, reg_data); break;
        case 30: SET_MSEC_SA_MAP_TCAM_30(sam_pkd.bytes.bytes, reg_data); break;
        case 31: SET_MSEC_SA_MAP_TCAM_31(sam_pkd.bytes.bytes, reg_data); break;

      default:
        break;
    }   

    /* Write the record back to the h/w */
    for(i = 0; i < sizeof(sam_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(sam_pkd.regs.regs[i]));
    }
   
    return CS_OK;

} /* leeds_macsec_ingress_update_sa_map */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to update the TCAM entry to the egress Security Association Map.
 *
 *  @param port       [I] -  The port number of the device to access. 
 *  @param cam_entry  [I] -  The CAM entry number
 *  @param ctxt_entry [I] -  The Context entry number (same as SA)
 *  @param enable     [I] -  Enable the entry flag, TRUE or FALSE
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_egress_update_sa_map(
    uint32  port,
    uint32  cam_entry,
    uint32  ctxt_entry,
    uint8   enable)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    
    leeds_macsec_sa_map_pkd_t sam_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress Security Association Map\n");
#endif

    memset(sam_pkd.bytes.bytes, 0, sizeof(sam_pkd));
   
    addr = LEEDS_MACSEC_EGRESS_STCAM_SA_MAP9;

    for(i = 0; i < sizeof(sam_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        sam_pkd.regs.regs[i] = ntohs(reg_data);
    }

    /* Set the field in the SAM record */
    if (TRUE == enable)
    {
      reg_data = ctxt_entry | 0x10;
    }
    else
    {
      reg_data = 0;
    }

    switch (cam_entry)
    {
        case 0 : SET_MSEC_SA_MAP_TCAM_00(sam_pkd.bytes.bytes, reg_data); break;
        case 1 : SET_MSEC_SA_MAP_TCAM_01(sam_pkd.bytes.bytes, reg_data); break;
        case 2 : SET_MSEC_SA_MAP_TCAM_02(sam_pkd.bytes.bytes, reg_data); break;
        case 3 : SET_MSEC_SA_MAP_TCAM_03(sam_pkd.bytes.bytes, reg_data); break;
        case 4 : SET_MSEC_SA_MAP_TCAM_04(sam_pkd.bytes.bytes, reg_data); break;
        case 5 : SET_MSEC_SA_MAP_TCAM_05(sam_pkd.bytes.bytes, reg_data); break;
        case 6 : SET_MSEC_SA_MAP_TCAM_06(sam_pkd.bytes.bytes, reg_data); break;
        case 7 : SET_MSEC_SA_MAP_TCAM_07(sam_pkd.bytes.bytes, reg_data); break;
        case 8 : SET_MSEC_SA_MAP_TCAM_08(sam_pkd.bytes.bytes, reg_data); break;
        case 9 : SET_MSEC_SA_MAP_TCAM_09(sam_pkd.bytes.bytes, reg_data); break;
        case 10: SET_MSEC_SA_MAP_TCAM_10(sam_pkd.bytes.bytes, reg_data); break;
        case 11: SET_MSEC_SA_MAP_TCAM_11(sam_pkd.bytes.bytes, reg_data); break;
        case 12: SET_MSEC_SA_MAP_TCAM_12(sam_pkd.bytes.bytes, reg_data); break;
        case 13: SET_MSEC_SA_MAP_TCAM_13(sam_pkd.bytes.bytes, reg_data); break;
        case 14: SET_MSEC_SA_MAP_TCAM_14(sam_pkd.bytes.bytes, reg_data); break;
        case 15: SET_MSEC_SA_MAP_TCAM_15(sam_pkd.bytes.bytes, reg_data); break;
        case 16: SET_MSEC_SA_MAP_TCAM_16(sam_pkd.bytes.bytes, reg_data); break;
        case 17: SET_MSEC_SA_MAP_TCAM_17(sam_pkd.bytes.bytes, reg_data); break;
        case 18: SET_MSEC_SA_MAP_TCAM_18(sam_pkd.bytes.bytes, reg_data); break;
        case 19: SET_MSEC_SA_MAP_TCAM_19(sam_pkd.bytes.bytes, reg_data); break;
        case 20: SET_MSEC_SA_MAP_TCAM_20(sam_pkd.bytes.bytes, reg_data); break;
        case 21: SET_MSEC_SA_MAP_TCAM_21(sam_pkd.bytes.bytes, reg_data); break;
        case 22: SET_MSEC_SA_MAP_TCAM_22(sam_pkd.bytes.bytes, reg_data); break;
        case 23: SET_MSEC_SA_MAP_TCAM_23(sam_pkd.bytes.bytes, reg_data); break;
        case 24: SET_MSEC_SA_MAP_TCAM_24(sam_pkd.bytes.bytes, reg_data); break;
        case 25: SET_MSEC_SA_MAP_TCAM_25(sam_pkd.bytes.bytes, reg_data); break;
        case 26: SET_MSEC_SA_MAP_TCAM_26(sam_pkd.bytes.bytes, reg_data); break;
        case 27: SET_MSEC_SA_MAP_TCAM_27(sam_pkd.bytes.bytes, reg_data); break;
        case 28: SET_MSEC_SA_MAP_TCAM_28(sam_pkd.bytes.bytes, reg_data); break;
        case 29: SET_MSEC_SA_MAP_TCAM_29(sam_pkd.bytes.bytes, reg_data); break;
        case 30: SET_MSEC_SA_MAP_TCAM_30(sam_pkd.bytes.bytes, reg_data); break;
        case 31: SET_MSEC_SA_MAP_TCAM_31(sam_pkd.bytes.bytes, reg_data); break;

      default:
        break;
    }   

    /* Write the record back to the h/w */
    for(i = 0; i < sizeof(sam_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(sam_pkd.regs.regs[i]));
    }
   
    return CS_OK;

} /* leeds_macsec_egress_update_sa_map */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to update a Frame Validation token. This method is used for both
 * ingress and egress token updates.
 *
 *  @param port   [I] -  The port number of the device to access. 
 *  @param token  [I] -  The token definition
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_iefv_tok_wr(
        uint32                                port,
        leeds_macsec_frame_valid_token_rec_t* tok)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_frame_valid_token_pkd_t tok_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress Frame Validation\n");
#endif

    memset(tok_pkd.bytes.bytes, 0, sizeof(tok_pkd));
   
    /* Set the fields in the packed Token record */
    SET_MSEC_FRAME_VALID_TOK_WORD(tok_pkd.bytes.bytes, tok->control_word);
    SET_MSEC_FRAME_VALID_TOK_CID(tok_pkd.bytes.bytes,  tok->ctxt_id);
    SET_MSEC_FRAME_VALID_TOK_OID(tok_pkd.bytes.bytes,  tok->output_id);
   
    switch (tok->frame_type) 
    {
      /*
      Note: use high numbered labels because their addresses are in descending order 
      */
      case e_leeds_macsec_ingress_controlled:
        addr = LEEDS_MACSEC_INGRESS_CONTROLLED_FRAME_STCAM_MISS_TOKEN5;
        break;

      case e_leeds_macsec_ingress_un_controlled:
        addr = LEEDS_MACSEC_INGRESS_UNCONTROLLED_FRAME_STCAM_MISS_TOKEN5;
        break;

      case e_leeds_macsec_ingress_invalid_frame:
        addr = LEEDS_MACSEC_INGRESS_STCAM_INVALID_FRAME_TOKEN5;
        break;

      case e_leeds_macsec_egress_security_miss:
        addr = LEEDS_MACSEC_EGRESS_STCAM_MISS_TOKEN5;
        break;

      default:
        /* invalid frame type */
        dbg_dump(stdout, "ERROR: leeds_macsec_iefv_tok_wr(), frame_type:%d\n", tok->frame_type);
        return CS_ERROR;
        break;
    }


    /* Write the Token back to the h/w */
    for(i = 0; i < sizeof(tok_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(tok_pkd.regs.regs[i]));
    }
   
    return CS_OK;

} /* leeds_macsec_iefv_tok_wr */

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read a Frame Validation token. This method is used for both
 * ingress and egress token reads.
 *
 *  @param port   [I] -  The port number of the device to access. 
 *  @param token  [I] -  The token definition
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_iefv_tok_rd(
        uint32                                port,
        leeds_macsec_frame_valid_token_rec_t* tok)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    
    leeds_macsec_frame_valid_token_pkd_t tok_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: ingress Frame Validation\n");
#endif

    memset(tok_pkd.bytes.bytes, 0, sizeof(tok_pkd));

    switch (tok->frame_type) 
    {
      /*
      Note: use high numbered labels because their addresses are in descending order 
      */
      case e_leeds_macsec_ingress_controlled:
        addr = LEEDS_MACSEC_INGRESS_CONTROLLED_FRAME_STCAM_MISS_TOKEN5;
        break;

      case e_leeds_macsec_ingress_un_controlled:
        addr = LEEDS_MACSEC_INGRESS_UNCONTROLLED_FRAME_STCAM_MISS_TOKEN5;
        break;

      case e_leeds_macsec_ingress_invalid_frame:
        addr = LEEDS_MACSEC_INGRESS_STCAM_INVALID_FRAME_TOKEN5;
        break;

      case e_leeds_macsec_egress_security_miss:
        addr = LEEDS_MACSEC_EGRESS_STCAM_MISS_TOKEN5;
        break;

      default:
        /* invalid frame type */
        dbg_dump(stdout, "ERROR: leeds_macsec_iefv_tok_wr(), frame_type:%d\n", tok->frame_type);
        return CS_ERROR;
        break;
    }

    for(i = 0; i < sizeof(tok_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        tok_pkd.regs.regs[i] = ntohs(reg_data);

    }

    /* Get the fields from the packed Token record */
    tok->control_word = GET_MSEC_FRAME_VALID_TOK_WORD(tok_pkd.bytes.bytes);
    tok->ctxt_id      = GET_MSEC_FRAME_VALID_TOK_CID(tok_pkd.bytes.bytes);
    tok->output_id    = GET_MSEC_FRAME_VALID_TOK_OID(tok_pkd.bytes.bytes);
   
    return CS_OK;

} /* leeds_macsec_iefv_tok_rd */



/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to write a single entry to the Ingress Classification 
 * Parser TCAM. 
 *
 *  @param port   [I] -  The port number of the device to access. 
 *  @param entry  [I] -  The entry within the TCAM to program (0-31). 
 *  @param cam    [I] -  The data to program within the entry. Refer to the leeds_macsec_ipr_tcam_entry_t 
 *      data structure for the layout of the data. 
 *  @param mask   [I] -  The 13 bit mask associated with the entry. With the exception of the TCI_AN 
 *      field only individual fields can be masked, not the bits within each field. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_ipr_cam_wr(
        uint32                        port,
        uint32                        entry,
        leeds_macsec_ipr_cam_entry_t* cam,
        leeds_macsec_ipr_cam_mask_t*  mask)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_ipr_cam_entry_pkd_t cam_pkd;
    leeds_macsec_ipr_cam_mask_pkd_t mask_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress parser\n");
#endif

    if(entry >= NUM_MACSEC_IPR_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }

    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));
   
    /* Set the fields in the packed TCAM entry  */
    SET_MSEC_IPR_CAM_PK_FE(cam_pkd.bytes.bytes, cam->fe);
    SET_MSEC_IPR_CAM_PK_ET(cam_pkd.bytes.bytes, cam->et);
    SET_MSEC_IPR_CAM_PK_TCI_AN(cam_pkd.bytes.bytes, cam->tci_an);
    SET_MSEC_IPR_CAM_PK_SA(cam_pkd.bytes.bytes, addr_to_uint64(cam->sa));
    SET_MSEC_IPR_CAM_PK_DA(cam_pkd.bytes.bytes, addr_to_uint64(cam->da));    
    SET_MSEC_IPR_CAM_PK_SCI(cam_pkd.bytes.bytes, cam->sci);
   
    /* Write the TCAM entry back to the h/w */
    addr = LEEDS_MACSEC_INGRESS_TCAM0 + (entry* (sizeof(cam_pkd.regs)/sizeof(uint16)));
    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(cam_pkd.regs.regs[i]));
    }
   
    /* Set the fields in the packed TCAM mask */
    SET_MSEC_IPR_CAM_MSK_PK_FE(mask_pkd.bytes.bytes, mask->fe);
    SET_MSEC_IPR_CAM_MSK_PK_ET(mask_pkd.bytes.bytes, mask->et);
    SET_MSEC_IPR_CAM_MSK_PK_TCI_AN(mask_pkd.bytes.bytes, mask->tci_an);
    SET_MSEC_IPR_CAM_MSK_PK_SA(mask_pkd.bytes.bytes, mask->sa);
    SET_MSEC_IPR_CAM_MSK_PK_DA(mask_pkd.bytes.bytes, mask->da);
    SET_MSEC_IPR_CAM_MSK_PK_SCI(mask_pkd.bytes.bytes, mask->sci);
   
    /* Write the TCAM entry back to the h/w */
    addr = LEEDS_MACSEC_INGRESS_TCAM_ENTRY_0_MASK + entry;
    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    leeds_reg_set(port, addr, htons(mask_pkd.regs.regs));

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read a single entry from the Ingress Classification 
 * Parser TCAM. 
 *
 *  @param port   [I] -  The port number to access. 
 *  @param entry  [I] -  The entry within the TCAM to read from (0-31). 
 *  @param cam    [O] -  The data read from the entry. 
 *  @param mask   [O] -  The mask associated with the entry. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ipr_cam_rd(
        uint32                        port,
        uint32                        entry,
        leeds_macsec_ipr_cam_entry_t* cam,
        leeds_macsec_ipr_cam_mask_t*  mask)
{
    uint32 addr;
    uint32 i;
    uint16 reg_data;
    
    /* Structures for unpacking the data and mask */
    leeds_macsec_ipr_cam_entry_pkd_t cam_pkd;
    leeds_macsec_ipr_cam_mask_pkd_t  mask_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: ingress parser\n");
#endif

    if(entry >= NUM_MACSEC_IPR_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }

    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));
    
    /* Calculate the address where the IPR
       CAM entry resides */
    addr = LEEDS_MACSEC_INGRESS_TCAM0 + (entry* (sizeof(cam_pkd.regs)/sizeof(uint16)));
    
    /* Read the packed entry from the h/w. It is stored
       in the MACSEC_INGRESS_TCAM[n] registers */
    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        cam_pkd.regs.regs[i] = ntohs(reg_data);
    }
    
    /*dbg_dump(stdout, "bytes = ");
    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint8); i++)
    {
        dbg_dump(stdout, "%02x ", cam_pkd.bytes.bytes[i]);
    }
    dbg_dump(stdout, "\n");*/
    
    cam->fe = GET_MSEC_IPR_CAM_PK_FE(cam_pkd.bytes.bytes);
    cam->et = GET_MSEC_IPR_CAM_PK_ET(cam_pkd.bytes.bytes);
    cam->tci_an = GET_MSEC_IPR_CAM_PK_TCI_AN(cam_pkd.bytes.bytes);
    uint64_to_addr(GET_MSEC_IPR_CAM_PK_SA(cam_pkd.bytes.bytes), cam->sa);
    uint64_to_addr(GET_MSEC_IPR_CAM_PK_DA(cam_pkd.bytes.bytes), cam->da);
    cam->sci = GET_MSEC_IPR_CAM_PK_SCI(cam_pkd.bytes.bytes);
    
    addr = LEEDS_MACSEC_INGRESS_TCAM_ENTRY_0_MASK + entry;
    leeds_reg_get(port, addr, &reg_data);
    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    mask_pkd.regs.regs = ntohs(reg_data);
    
    mask->fe = GET_MSEC_IPR_CAM_MSK_PK_FE(mask_pkd.bytes.bytes);
    mask->et = GET_MSEC_IPR_CAM_MSK_PK_ET(mask_pkd.bytes.bytes);
    mask->tci_an = GET_MSEC_IPR_CAM_MSK_PK_TCI_AN(mask_pkd.bytes.bytes);
    mask->sa = GET_MSEC_IPR_CAM_MSK_PK_SA(mask_pkd.bytes.bytes);
    mask->da = GET_MSEC_IPR_CAM_MSK_PK_DA(mask_pkd.bytes.bytes);
    mask->sci = GET_MSEC_IPR_CAM_MSK_PK_SCI(mask_pkd.bytes.bytes);
    
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program multiple entries within the Parser Classification 
 * CAM in the ingress direction. 
 *
 *  @param port         [I] -  The port to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of data to store within the TCAM. 
 *  @param masks        [I] -  The array of masks to store. With the exception of TCI_AN field the mask 
 *      is only capable of masking individual fields, not bits within each field. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_ipr_cam_tbl_wr(
        uint32                       port,
        uint32                       base,
        uint32                       num_entries,
        leeds_macsec_ipr_cam_entry_t entries[],
        leeds_macsec_ipr_cam_mask_t  masks[])
{
    /* FUNCTION PSEUDOCODE: */
    uint32 i;
    cs_status rc = CS_OK;
    
    if((base + num_entries) > NUM_MACSEC_IPR_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_ipr_cam_wr(port, i, &entries[i], &masks[i]);
    
        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
    

}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program an entry within the Ingress Context Table.
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry within the table to access. 
 *  @param data   [I] -  The context record to write to the table. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 *
 */
cs_status leeds_macsec_ict_wr(
        uint32                   port,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    uint32 i;
    uint32 addr;
    uint64 key_lo, key_hi;  
    uint8  *ptr_lo, *ptr_hi;
    leeds_macsec_ctxt_rec_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress context\n");
#endif

    if(entry > NUM_MACSEC_ICT_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));

    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      *ptr_lo++ = data->akey[i];
      *ptr_hi++ = data->akey[i+8];
    }
    SET_MSEC_CTX_RC_PK_AKEY_LO(rec_pkd.bytes.bytes, key_lo);
    SET_MSEC_CTX_RC_PK_AKEY_HI(rec_pkd.bytes.bytes, key_hi);

    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      *ptr_lo++ = data->hkey[i];
      *ptr_hi++ = data->hkey[i+8];
    }
    SET_MSEC_CTX_RC_PK_HKEY_LO(      rec_pkd.bytes.bytes, key_lo);
    SET_MSEC_CTX_RC_PK_HKEY_HI(      rec_pkd.bytes.bytes, key_hi);

    SET_MSEC_CTX_RC_PK_IV1(          rec_pkd.bytes.bytes, data->iv1);
    SET_MSEC_CTX_RC_PK_IV0(          rec_pkd.bytes.bytes, data->iv0);
    SET_MSEC_CTX_RC_PK_SEQ_NUM_MASK( rec_pkd.bytes.bytes, data->seq_num_mask);
    SET_MSEC_CTX_RC_PK_SEQ_NUM(      rec_pkd.bytes.bytes, data->seq_num);
    SET_MSEC_CTX_RC_PK_CTXT_ID(      rec_pkd.bytes.bytes, data->ctxt_id);
    SET_MSEC_CTX_RC_PK_CTRL_WORD(    rec_pkd.bytes.bytes, data->ctrl_word);

    addr = LEEDS_MACSEC_INGRESS_CTX_MEM0 + (32 * entry);

    /* Write the record back to registers */
    for(i = 0; i < 32; i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read an entry from the Ingress Context Table.
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry within the table to access. 
 *  @param data   [O] -  The data read from the table. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ict_rd(
        uint32                   port,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    uint64 key_lo, key_hi;  
    uint8  *ptr_lo, *ptr_hi;
    leeds_macsec_ctxt_rec_pkd_t rec_pkd;
   
#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: ingress context\n");
#endif
 
    if(entry > NUM_MACSEC_ICT_ENTRIES)
    {
      return CS_BOUNDS;
    }
 
    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));
 
    addr = LEEDS_MACSEC_INGRESS_CTX_MEM0 + (32 * entry);
 
    /* Read the record from registers */
    for(i = 0; i < 32; i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }
 
    key_lo             = GET_MSEC_CTX_RC_PK_HKEY_LO(rec_pkd.bytes.bytes);
    key_hi             = GET_MSEC_CTX_RC_PK_HKEY_HI(rec_pkd.bytes.bytes);
    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      data->hkey[i]   = *ptr_lo++;
      data->hkey[i+8] = *ptr_hi++;
    }

    key_lo             = GET_MSEC_CTX_RC_PK_AKEY_LO(rec_pkd.bytes.bytes);
    key_hi             = GET_MSEC_CTX_RC_PK_AKEY_HI(rec_pkd.bytes.bytes);
    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      data->akey[i]   = *ptr_lo++;
      data->akey[i+8] = *ptr_hi++;
    }

    data->iv1          = GET_MSEC_CTX_RC_PK_IV1(rec_pkd.bytes.bytes);
    data->iv0          = GET_MSEC_CTX_RC_PK_IV0(rec_pkd.bytes.bytes);
    data->seq_num_mask = GET_MSEC_CTX_RC_PK_SEQ_NUM_MASK(rec_pkd.bytes.bytes);
    data->seq_num      = GET_MSEC_CTX_RC_PK_SEQ_NUM(rec_pkd.bytes.bytes);
    data->ctxt_id      = GET_MSEC_CTX_RC_PK_CTXT_ID(rec_pkd.bytes.bytes);
    data->ctrl_word    = GET_MSEC_CTX_RC_PK_CTRL_WORD(rec_pkd.bytes.bytes);

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to configure the entire Ingress Context table in one operation. 
 *
 *  @param port         [I] -  The port to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of data to store within the context memory. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 * 
 */
cs_status leeds_macsec_ict_tbl_wr(
        uint32                  port,
        uint32                  base,
        uint32                  num_entries,
        leeds_macsec_ctxt_rec_t entries[])
{
    uint32 i;
    cs_status rc = CS_OK;
    
    if((base + num_entries) > NUM_MACSEC_ICT_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_ict_wr(port, i, &(entries[i]));
    
        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program the configuration registers into the MACsec core. 
 * 
 *  @param port  [I] -  The port to access. 
 *  @param data  [I] -  The register data to program. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_icc_wr(
        uint32                    port,
        uint32                    entry,
        leeds_macsec_core_ctxt_t* data)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_core_ctxt_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress core context\n");
#endif

    memset(&rec_pkd, 0, sizeof(rec_pkd));

    SET_MSEC_CORE_CTX_RC_PK_TOKEN_CTRL_STAT(rec_pkd.bytes.bytes, data->token_ctl_stat );
    SET_MSEC_CORE_CTX_RC_PK_PROT_AL_ENB(rec_pkd.bytes.bytes, data->prot_al_enb);
    SET_MSEC_CORE_CTX_RC_PK_CTXT_CONTROL(rec_pkd.bytes.bytes, data->ctxt_control);
    SET_MSEC_CORE_CTX_RC_PK_CTXT_STAT(rec_pkd.bytes.bytes, data->ctxt_stat);
    SET_MSEC_CORE_CTX_RC_PK_INTR_CTL_STAT(rec_pkd.bytes.bytes, data->intr_ctl_stat);
    SET_MSEC_CORE_CTX_RC_PK_SW_INTR(rec_pkd.bytes.bytes, data->sw_intr);
    SET_MSEC_CORE_CTX_RC_PK_SEQ_NUM_THRESH(rec_pkd.bytes.bytes, data->seq_num_thresh);
    SET_MSEC_CORE_CTX_RC_PK_TYPE(rec_pkd.bytes.bytes, data->type);
    SET_MSEC_CORE_CTX_RC_PK_VERSION(rec_pkd.bytes.bytes, data->version);

    addr = LEEDS_MACSEC_INGRESS_CORE_HOST0;

    /* Write the record back to registers */
    for(i = 0; i < sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read the configuration registers from the MACsec core. 
 * 
 *  @param port  [I] -  The port to access. 
 *  @param data  [O] -  The configuration data read from the device. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_icc_rd(
        uint32 port,
        uint32 entry,
        leeds_macsec_core_ctxt_t* data)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    
    leeds_macsec_core_ctxt_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: ingress core context\n");
#endif

    memset(&rec_pkd, 0, sizeof(rec_pkd));

    addr = LEEDS_MACSEC_INGRESS_CORE_HOST0;

    /* Read the record from registers */
    for(i = 0; i < sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }

    /* Now copy the record over */
    data->token_ctl_stat = GET_MSEC_CORE_CTX_RC_PK_TOKEN_CTRL_STAT(rec_pkd.bytes.bytes);
    data->prot_al_enb    = GET_MSEC_CORE_CTX_RC_PK_PROT_AL_ENB(rec_pkd.bytes.bytes);
    data->ctxt_control   = GET_MSEC_CORE_CTX_RC_PK_CTXT_CONTROL(rec_pkd.bytes.bytes);
    data->ctxt_stat      = GET_MSEC_CORE_CTX_RC_PK_CTXT_STAT(rec_pkd.bytes.bytes);
    data->intr_ctl_stat  = GET_MSEC_CORE_CTX_RC_PK_INTR_CTL_STAT(rec_pkd.bytes.bytes);
    data->sw_intr        = GET_MSEC_CORE_CTX_RC_PK_SW_INTR(rec_pkd.bytes.bytes);
    data->seq_num_thresh = GET_MSEC_CORE_CTX_RC_PK_SEQ_NUM_THRESH(rec_pkd.bytes.bytes);
    data->type           = GET_MSEC_CORE_CTX_RC_PK_TYPE(rec_pkd.bytes.bytes);
    data->version        = GET_MSEC_CORE_CTX_RC_PK_VERSION(rec_pkd.bytes.bytes);

  return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program all or part of the Ingress Core Context table 
 * in one operation. There really is only a single entry in the table but the
 * interface is kept the same for consistency with the other tables.
 *
 *  @param port         [I] -  The port number of the device to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of entries to store in the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_icc_tbl_wr(
        uint32                    port,
        uint32                    base,
        uint32                    num_entries,
        leeds_macsec_core_ctxt_t  entries[])
{
    uint32 i;
    cs_status rc = CS_OK;

    if((base + num_entries) > NUM_MACSEC_ICC_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_icc_wr(port, i, &(entries[i]));

        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program an entry within the Ingress Rules token table. 
 * 
 *  @param port   [I] -  The port number of the device to access. 
 *  @param entry  [I] -  The entry number of the rule to access. 
 *  @param data   [I] -  The rule token to update. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_irt_wr(
        uint32                port,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_token_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: ingress rules\n");
#endif

    if(entry > NUM_MACSEC_IRT_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));

    SET_MSEC_TKN_PK_TOKEN_TYPE(rec_pkd.bytes.bytes,  data->token_type);
    SET_MSEC_TKN_PK_PASS(rec_pkd.bytes.bytes,        data->pass);
    SET_MSEC_TKN_PK_DIRECTION(rec_pkd.bytes.bytes,   data->direction);
    SET_MSEC_TKN_PK_ES(rec_pkd.bytes.bytes,          data->es);
    SET_MSEC_TKN_PK_SC(rec_pkd.bytes.bytes,          data->sc);
    SET_MSEC_TKN_PK_SCB(rec_pkd.bytes.bytes,         data->scb);
    SET_MSEC_TKN_PK_TOO(rec_pkd.bytes.bytes,         data->too);
    SET_MSEC_TKN_PK_ECO(rec_pkd.bytes.bytes,         data->eco);
    SET_MSEC_TKN_PK_CO(rec_pkd.bytes.bytes,          data->co);
    SET_MSEC_TKN_PK_CID_UPDATE(rec_pkd.bytes.bytes,  data->cid_update);
    SET_MSEC_TKN_PK_OID_VALID(rec_pkd.bytes.bytes,   data->oid_valid);
    SET_MSEC_TKN_PK_LEN_VALID(rec_pkd.bytes.bytes,   data->len_valid);
    SET_MSEC_TKN_PK_INP_PKT_LEN(rec_pkd.bytes.bytes, data->inp_pkt_len);
    SET_MSEC_TKN_PK_CONTEXT_PTR(rec_pkd.bytes.bytes, data->context_ptr);
    SET_MSEC_TKN_PK_OUTPUT_ID(rec_pkd.bytes.bytes,   data->output_id);
    SET_MSEC_TKN_PK_EXTENDED_CO(rec_pkd.bytes.bytes, data->extended_co);

    addr = LEEDS_MACSEC_INGRESS_TOKEN_MEM0 + (entry * sizeof(rec_pkd.regs)/sizeof(uint16));

    /* Write the record back to registers */
    for(i = 0; i < sizeof(leeds_macsec_token_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read an entry from within the Ingress Rules Token table. 
 * 
 *  @param port   [I] -  The port number of the device to access. 
 *  @param entry  [I] -  The entry number of the rule to read. 
 *  @param data   [O] -  The rule token data. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_irt_rd(
        uint32                port,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    uint32 addr;
    uint32 i;
    uint16 reg_data;
    
    /* Structures for unpacking the data and mask */
    leeds_macsec_token_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: ingress rules\n");
#endif

    if(entry > NUM_MACSEC_IRT_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));
    
    addr = LEEDS_MACSEC_INGRESS_TOKEN_MEM0 + (entry * (sizeof(rec_pkd)/sizeof(uint16)));
    
    /* Read the packed entry from the h/w. */
    for(i = 0; i < sizeof(rec_pkd.regs)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }

    data->token_type  = GET_MSEC_TKN_PK_TOKEN_TYPE(rec_pkd.bytes.bytes);
    data->pass        = GET_MSEC_TKN_PK_PASS(rec_pkd.bytes.bytes);
    data->direction   = GET_MSEC_TKN_PK_DIRECTION(rec_pkd.bytes.bytes);
    data->es          = GET_MSEC_TKN_PK_ES(rec_pkd.bytes.bytes);
    data->sc          = GET_MSEC_TKN_PK_SC(rec_pkd.bytes.bytes);
    data->scb         = GET_MSEC_TKN_PK_SCB(rec_pkd.bytes.bytes);
    data->too         = GET_MSEC_TKN_PK_TOO(rec_pkd.bytes.bytes);
    data->eco         = GET_MSEC_TKN_PK_ECO(rec_pkd.bytes.bytes);
    data->co          = GET_MSEC_TKN_PK_CO(rec_pkd.bytes.bytes);
    data->cid_update  = GET_MSEC_TKN_PK_CID_UPDATE(rec_pkd.bytes.bytes);
    data->oid_valid   = GET_MSEC_TKN_PK_OID_VALID(rec_pkd.bytes.bytes);
    data->len_valid   = GET_MSEC_TKN_PK_LEN_VALID(rec_pkd.bytes.bytes);
    data->inp_pkt_len = GET_MSEC_TKN_PK_INP_PKT_LEN(rec_pkd.bytes.bytes);
    data->context_ptr = GET_MSEC_TKN_PK_CONTEXT_PTR(rec_pkd.bytes.bytes);
    data->output_id   = GET_MSEC_TKN_PK_OUTPUT_ID(rec_pkd.bytes.bytes);
    data->extended_co = GET_MSEC_TKN_PK_EXTENDED_CO(rec_pkd.bytes.bytes);

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program all or part of the Ingress Rules Token table 
 * in one operation. 
 *
 *  @param port         [I] -  The port number of the device to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of entries to store in the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_irt_tbl_wr(
        uint32                port,
        uint32                base,
        uint32                num_entries,
        leeds_macsec_token_t  entries[])
{
    uint32 i;
    cs_status rc = CS_OK;

    if((base + num_entries) > NUM_MACSEC_IRT_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_irt_wr(port, i, &(entries[i]));

        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program an entry in the Consistency Check CAM. 
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry within the TCAM being programmed. 
 *  @param cam    [I] -  The data to program within the TCAM entry. 
 *  @param mask   [I] -  A mask that can mask individual fields within the entry. The mask is not 
 *      capable of masking out individual bits within the TCAM data fields. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_chk_cam_wr(
            uint32                        port,
            uint32                        entry,
            leeds_macsec_chk_cam_entry_t* cam,
            leeds_macsec_chk_cam_mask_t*  mask)
{
    /* FUNCTION PSEUDOCODE: */
    leeds_macsec_chk_cam_entry_pkd_t cam_pkd;
    leeds_macsec_chk_cam_mask_pkd_t  mask_pkd;
    uint32 addr;
    uint16 enable_bits;
    uint32 i;
    
#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: CC\n");
#endif

    if(entry > NUM_MACSEC_CHK_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));

    /* 
    dbg_dump(stdout, "  chk_cam_wr: %d\n", entry);
      dbg_dump(stdout, "    -> cam->et  = %x, cam->ev  = %x, cam->sai  = %x, cam->sh = %x, cam->tg = %x, cam->vlan = %x\n",
           cam->et, cam->ev, cam->sai, cam->sh, cam->tg, cam->vlan);
      dbg_dump(stdout, "    -> mask->et = %x, mask->ev = %x, mask->sai = %x, mask->sh = %x, mask->tg = %x, mask->vlan = %x\n",
           mask->et, mask->ev, mask->sai, mask->sh, mask->tg, mask->vlan); 
    */ 
    /* Copy the entry into a packed format. This is
       hidden from the caller to simplify the external
       API. */
    SET_MSEC_CHK_CAM_PK_ET(cam_pkd.bytes.bytes, cam->et);
    SET_MSEC_CHK_CAM_PK_EV(cam_pkd.bytes.bytes, cam->ev);
    SET_MSEC_CHK_CAM_PK_SAI(cam_pkd.bytes.bytes, cam->sai);
    SET_MSEC_CHK_CAM_PK_SH(cam_pkd.bytes.bytes, cam->sh);
    SET_MSEC_CHK_CAM_PK_TG(cam_pkd.bytes.bytes, cam->tg);
    SET_MSEC_CHK_CAM_PK_VLAN(cam_pkd.bytes.bytes, cam->vlan);

    SET_MSEC_CHK_CAM_MSK_PK_SAI( mask_pkd.bytes.bytes, mask->sai);
    SET_MSEC_CHK_CAM_MSK_PK_SH(  mask_pkd.bytes.bytes, mask->sh);
    SET_MSEC_CHK_CAM_MSK_PK_VLAN(mask_pkd.bytes.bytes, mask->vlan);
    SET_MSEC_CHK_CAM_MSK_PK_TG(  mask_pkd.bytes.bytes, mask->tg);
    SET_MSEC_CHK_CAM_MSK_PK_EV(  mask_pkd.bytes.bytes, mask->ev);
    SET_MSEC_CHK_CAM_MSK_PK_ET(  mask_pkd.bytes.bytes, mask->et);

    /* Store the CAM data to h/w */
    addr = LEEDS_MACSEC_INGRESS_CC_TCAM0 + (entry * 4);

    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(cam_pkd.regs.regs[i]));
    }
    
    /* Store the mask to h/w */
    addr = LEEDS_MACSEC_INGRESS_CC_TCAM_ENTRY_0_MASK + entry;

    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    leeds_reg_set(port, addr, htons(mask_pkd.regs.regs)); 

    /* Enable the entry in the TCAM using the
       MACSEC_INGRESS_CC_TCAM_Entry_Valid register. Need to
       read the entries first so that we don't clear any
       already enabled entries. 
    */
    addr = LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Valid;

    leeds_reg_get(port, addr, &enable_bits);
    enable_bits |= (1 << entry);
    leeds_reg_set(port, addr, enable_bits);
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read an entry from the Consistency Check CAM. The mask 
 * field is only capable of masking entries on a per field basis rather than masking 
 * out the entire entry. A global mask can be configured that applies to all entries 
 * that can touch all bits of the CAM. 
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry of the TCAM to read (0-15). 
 *  @param cam    [O] -  The data stored within the CAM entry. 
 *  @param mask   [O] -  The CC TCAM only supports a per field mask that is 6 bits long. This can 
 *      be used to mask out individual fields but not parts of the field. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_chk_cam_rd(
            uint32                        port,
            uint32                        entry,
            leeds_macsec_chk_cam_entry_t* cam,
            leeds_macsec_chk_cam_mask_t*  mask)
{
    uint32 addr;
    uint32 i;
    uint16 data;
    
    /* Structures for unpacking the data and mask */
    leeds_macsec_chk_cam_entry_pkd_t cam_pkd;
    leeds_macsec_chk_cam_mask_pkd_t  mask_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: CC\n");
#endif

    if(entry >= NUM_MACSEC_CHK_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));
    
    /* Calculate the address where the consistency
       check cam entry resides */
    addr = LEEDS_MACSEC_INGRESS_CC_TCAM0 + (entry*4);

    /* There are actually only three registers per entry
     * TCAM0, TCAM1, and TCAM2. Don't attempt to read
     * the fourth address or we'll get an MPIF timeout */ 
    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        uint16 reg_data = 0;
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        cam_pkd.regs.regs[i] = ntohs(reg_data);
    }
    
    /* dbg_dump(stdout, "bytes = \n");
       for(i = 0; i < 8; i++)
       {
           dbg_dump(stdout, "%02x ", cam_pkd.bytes.bytes[i]);
       }
       dbg_dump(stdout, "\n"); 
    */
    
    /* Now, unpack the CAM entry */
    cam->et = GET_MSEC_CHK_CAM_PK_ET(cam_pkd.bytes.bytes);
    cam->ev = GET_MSEC_CHK_CAM_PK_EV(cam_pkd.bytes.bytes);
    cam->sai = GET_MSEC_CHK_CAM_PK_SAI(cam_pkd.bytes.bytes);
    cam->sh  = GET_MSEC_CHK_CAM_PK_SH(cam_pkd.bytes.bytes);
    cam->tg  = GET_MSEC_CHK_CAM_PK_TG(cam_pkd.bytes.bytes);
    cam->vlan = GET_MSEC_CHK_CAM_PK_VLAN(cam_pkd.bytes.bytes);
    
    /* Read the packed mask from the h/w. It is stored
       in the MACSEC_INGRESS_CC_TCAM_ENTRY_n_MASK registers */
    addr = LEEDS_MACSEC_INGRESS_CC_TCAM_ENTRY_0_MASK + entry;

    leeds_reg_get(port, addr, &data);

    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    mask_pkd.regs.regs = ntohs(data);

    /* Now unpack the mask */
    mask->et = GET_MSEC_CHK_CAM_MSK_PK_ET(mask_pkd.bytes.bytes);
    mask->ev = GET_MSEC_CHK_CAM_MSK_PK_EV(mask_pkd.bytes.bytes);
    mask->sai = GET_MSEC_CHK_CAM_MSK_PK_SAI(mask_pkd.bytes.bytes);
    mask->sh = GET_MSEC_CHK_CAM_MSK_PK_SH(mask_pkd.bytes.bytes);
    mask->tg = GET_MSEC_CHK_CAM_MSK_PK_TG(mask_pkd.bytes.bytes);
    mask->vlan = GET_MSEC_CHK_CAM_MSK_PK_VLAN(mask_pkd.bytes.bytes);
    
    /*
    dbg_dump(stdout, "  chk_cam_rd: %d\n", entry);
       dbg_dump(stdout, "    -> cam->et  = %x, cam->ev  = %x, cam->sai  = %x, cam->sh = %x, cam->tg = %x, cam->vlan = %x\n",
              cam->et, cam->ev, cam->sai, cam->sh, cam->tg, cam->vlan);
       dbg_dump(stdout, "    -> mask->et = %x, mask->ev = %x, mask->sai = %x, mask->sh = %x, mask->tg = %x, mask->vlan = %x\n",
              mask->et, mask->ev, mask->sai, mask->sh, mask->tg, mask->vlan); 
    */ 
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program multiple entries within the Consistency Check 
 * (CC) CAM in the ingress direction. 
 *
 *  @param port         [I] -  The port to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of data to store within the TCAM. 
 *  @param masks        [I] -  The array of masks to store. Each mask is actually 6 bits and is only capable 
 *      of masking individual fields, not bits within each field. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_chk_cam_tbl_wr(
        uint32                       port,
        uint32                       base,
        uint32                       num_entries,
        leeds_macsec_chk_cam_entry_t entries[],
        leeds_macsec_chk_cam_mask_t  masks[])
{
    /* FUNCTION PSEUDOCODE: */
    uint32 i;
    cs_status rc = CS_OK;
    
    if((base + num_entries) > NUM_MACSEC_CHK_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        leeds_macsec_chk_cam_entry_t* entry = &(entries[i]);
        leeds_macsec_chk_cam_mask_t* mask = &(masks[i]);
    
        cs_status cd = leeds_macsec_chk_cam_wr(port, i, entry, mask);
    
        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to write a single entry within the Egress Classification 
 * Parser TCAM. 
 *
 *  @param port   [I] -  The port number to access. 
 *  @param entry  [I] -  The entry within the TCAM to program (0-31). 
 *  @param data   [I] -  The data to program within the entry. 
 *  @param mask   [I] -  The mask associated with the entry, only individual fields can be masked, 
 *      not the bits within each field. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_epr_cam_wr(
        uint32                        port,
        uint32                        entry,
        leeds_macsec_epr_cam_entry_t* cam,
        leeds_macsec_epr_cam_mask_t*  mask)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_epr_cam_entry_pkd_t cam_pkd;
    leeds_macsec_epr_cam_mask_pkd_t mask_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: egress parser\n");
#endif

    if(entry > NUM_MACSEC_EPR_CAM_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));
    
    SET_MSEC_EPR_CAM_PK_VLAN(cam_pkd.bytes.bytes, cam->vlan);
    SET_MSEC_EPR_CAM_PK_ET(cam_pkd.bytes.bytes, cam->et);
    SET_MSEC_EPR_CAM_PK_SA(cam_pkd.bytes.bytes, addr_to_uint64(cam->sa));
    SET_MSEC_EPR_CAM_PK_DA(cam_pkd.bytes.bytes, addr_to_uint64(cam->da));
    
    addr = LEEDS_MACSEC_EGRESS_TCAM0 + (entry*(sizeof(cam_pkd.regs)/sizeof(uint16)));

    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        leeds_reg_set(port, addr+i, htons(cam_pkd.regs.regs[i]));
    }
    
    SET_MSEC_EPR_CAM_MSK_PK_VLAN(mask_pkd.bytes.bytes, mask->vlan);
    SET_MSEC_EPR_CAM_MSK_PK_ET(mask_pkd.bytes.bytes, mask->et);
    SET_MSEC_EPR_CAM_MSK_PK_SA(mask_pkd.bytes.bytes, mask->sa);
    SET_MSEC_EPR_CAM_MSK_PK_DA(mask_pkd.bytes.bytes, mask->da);
    
    addr = LEEDS_MACSEC_EGRESS_TCAM_ENTRY_0_MASK + entry;
    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    leeds_reg_set(port, addr, htons(mask_pkd.regs.regs));
   
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read a single entry within the Egress Classification 
 * Parser TCAM. 
 *
 *  @param port   [I] -  The port number to access. 
 *  @param entry  [I] -  The entry within the TCAM to read from (0-31). 
 *  @param data   [I] -  The data read from the TCAM entry. 
 *  @param mask   [I] -  The mask associated with the TCAM entry. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_epr_cam_rd(
        uint32                        port,
        uint32                        entry,
        leeds_macsec_epr_cam_entry_t* cam,
        leeds_macsec_epr_cam_mask_t*  mask)
{
    uint32 addr;
    uint32 i;
    uint16 reg_data;
    
    /* Structures for unpacking the data and mask */
    leeds_macsec_epr_cam_entry_pkd_t cam_pkd;
    leeds_macsec_epr_cam_mask_pkd_t  mask_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: egress parser\n");
#endif

    if(entry > NUM_MACSEC_EPR_CAM_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(cam_pkd.bytes.bytes, 0, sizeof(cam_pkd));
    memset(mask_pkd.bytes.bytes, 0, sizeof(mask_pkd));
    
    /* Calculate the address where the IPR
       CAM entry resides */
    addr = LEEDS_MACSEC_EGRESS_TCAM0 + (entry* (sizeof(cam_pkd.regs)/sizeof(uint16)));
    
    /* Read the packed entry from the h/w. It is stored
       in the MACSEC_INGRESS_TCAM[n] registers */
    for(i = 0; i < sizeof(cam_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        cam_pkd.regs.regs[i] = ntohs(reg_data);
    }
    
    cam->vlan    = GET_MSEC_EPR_CAM_PK_VLAN(cam_pkd.bytes.bytes);
    cam->et      = GET_MSEC_EPR_CAM_PK_ET(cam_pkd.bytes.bytes);
    uint64_to_addr(GET_MSEC_EPR_CAM_PK_SA(cam_pkd.bytes.bytes), cam->sa);
    uint64_to_addr(GET_MSEC_EPR_CAM_PK_DA(cam_pkd.bytes.bytes), cam->da);
    
    addr = LEEDS_MACSEC_EGRESS_TCAM_ENTRY_0_MASK + entry;
    leeds_reg_get(port, addr, &reg_data);
    /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
    mask_pkd.regs.regs = ntohs(reg_data);

    mask->vlan    = GET_MSEC_EPR_CAM_MSK_PK_VLAN(mask_pkd.bytes.bytes);
    mask->et      = GET_MSEC_EPR_CAM_MSK_PK_ET(mask_pkd.bytes.bytes);
    mask->sa      = GET_MSEC_EPR_CAM_MSK_PK_SA(mask_pkd.bytes.bytes);
    mask->da      = GET_MSEC_EPR_CAM_MSK_PK_DA(mask_pkd.bytes.bytes);

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program multiple entries within the Parser Classification 
 * CAM in the egress direction. 
 *
 *  @param port         [I] -  The port to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of data to store within the TCAM. 
 *  @param masks        [I] -  The array of masks to store. With the exception of TCI_AN field the mask 
 *      is only capable of masking individual fields, not bits within each field. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *      
 *
 */
cs_status leeds_macsec_epr_cam_tbl_wr(
        uint32                       port,
        uint32                       base,
        uint32                       num_entries,
        leeds_macsec_epr_cam_entry_t entries[],
        leeds_macsec_epr_cam_mask_t  masks[])
{
    uint32 i;
    cs_status rc = CS_OK;
    
    if((base + num_entries) > NUM_MACSEC_EPR_CAM_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_epr_cam_wr(port, i, &entries[i], &masks[i]);
    
        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 * 
 * This method is called to program an entry within the Egress Context Table used 
 * by the MACsec core. 
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry within the table to access. 
 *  @param data   [I] -  The data write to the table. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ect_wr(
        uint32                   port,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    uint32 i;
    uint32 addr;
    uint64 key_lo, key_hi;  
    uint8  *ptr_lo, *ptr_hi;
    leeds_macsec_ctxt_rec_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: egress context\n");
#endif

    if(entry > NUM_MACSEC_ECT_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));

    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      *ptr_lo++ = data->akey[i];
      *ptr_hi++ = data->akey[i+8];
    }
    SET_MSEC_CTX_RC_PK_AKEY_LO(rec_pkd.bytes.bytes, key_lo);
    SET_MSEC_CTX_RC_PK_AKEY_HI(rec_pkd.bytes.bytes, key_hi);

    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      *ptr_lo++ = data->hkey[i];
      *ptr_hi++ = data->hkey[i+8];
    }
    SET_MSEC_CTX_RC_PK_HKEY_LO(rec_pkd.bytes.bytes, key_lo);
    SET_MSEC_CTX_RC_PK_HKEY_HI(rec_pkd.bytes.bytes, key_hi);

    SET_MSEC_CTX_RC_PK_IV1(rec_pkd.bytes.bytes, data->iv1);
    SET_MSEC_CTX_RC_PK_IV0(rec_pkd.bytes.bytes, data->iv0);
    SET_MSEC_CTX_RC_PK_SEQ_NUM_MASK(rec_pkd.bytes.bytes, data->seq_num_mask);
    SET_MSEC_CTX_RC_PK_SEQ_NUM(rec_pkd.bytes.bytes, data->seq_num);
    SET_MSEC_CTX_RC_PK_CTXT_ID(rec_pkd.bytes.bytes, data->ctxt_id);
    SET_MSEC_CTX_RC_PK_CTRL_WORD(rec_pkd.bytes.bytes, data->ctrl_word); 
  
    addr = LEEDS_MACSEC_EGRESS_CTX_MEM0 + (32 * entry);
  
    /* Write the record back to registers */
    for(i = 0; i < 32; i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }
  
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read an entry from within the Egress Context Table.
 *
 *  @param port   [I] -  The port to access. 
 *  @param entry  [I] -  The entry within the table to access. 
 *  @param data   [O] -  The data read from the table. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ect_rd(
        uint32                   port,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    uint64 key_lo, key_hi;  
    uint8  *ptr_lo, *ptr_hi;
    leeds_macsec_ctxt_rec_pkd_t rec_pkd;
 
#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: egress context\n");
#endif

    if(entry > NUM_MACSEC_ECT_ENTRIES)
    {
      return CS_BOUNDS;
    }

    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));

    addr = LEEDS_MACSEC_EGRESS_CTX_MEM0 + (32 * entry);

    /* Read the record from registers */
    for(i = 0; i < 32; i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }

    key_lo             = GET_MSEC_CTX_RC_PK_HKEY_LO(rec_pkd.bytes.bytes);
    key_hi             = GET_MSEC_CTX_RC_PK_HKEY_HI(rec_pkd.bytes.bytes);
    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      data->hkey[i]   = *ptr_lo++;
      data->hkey[i+8] = *ptr_hi++;
    }

    key_lo             = GET_MSEC_CTX_RC_PK_AKEY_LO(rec_pkd.bytes.bytes);
    key_hi             = GET_MSEC_CTX_RC_PK_AKEY_HI(rec_pkd.bytes.bytes);
    ptr_lo = (uint8 *)&key_lo;
    ptr_hi = (uint8 *)&key_hi;
    for(i=0; i<8; i++) {
      data->akey[i]   = *ptr_lo++;
      data->akey[i+8] = *ptr_hi++;
    }

    data->iv1          = GET_MSEC_CTX_RC_PK_IV1(rec_pkd.bytes.bytes);
    data->iv0          = GET_MSEC_CTX_RC_PK_IV0(rec_pkd.bytes.bytes);
    data->seq_num_mask = GET_MSEC_CTX_RC_PK_SEQ_NUM_MASK(rec_pkd.bytes.bytes);
    data->seq_num      = GET_MSEC_CTX_RC_PK_SEQ_NUM(rec_pkd.bytes.bytes);
    data->ctxt_id      = GET_MSEC_CTX_RC_PK_CTXT_ID(rec_pkd.bytes.bytes);
    data->ctrl_word    = GET_MSEC_CTX_RC_PK_CTRL_WORD(rec_pkd.bytes.bytes);

    return CS_OK;
}



/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to configure the entire Egress Context table in one operation. 
 * 
 *  @param port         [I] -  The port to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of data to store within the context memory. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ect_tbl_wr(
        uint32                   port,
        uint32                   base,
        uint32                   num_entries,
        leeds_macsec_ctxt_rec_t  entries[])
{
    uint32 i;
    cs_status rc = CS_OK;
    
    if((base + num_entries) > NUM_MACSEC_ECT_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_ect_wr(port, i, &(entries[i]));
    
        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program the configuration registers for the MACsec core. 
 * 
 *  @param port  [I] -  The port to access. 
 *  @param data  [I] -  The data to program. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ecc_wr(
        uint32                    port,
        uint32                    entry,
        leeds_macsec_core_ctxt_t* data)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_core_ctxt_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: egress core context\n");
#endif

    memset(&rec_pkd, 0, sizeof(rec_pkd));

    SET_MSEC_CORE_CTX_RC_PK_TOKEN_CTRL_STAT(rec_pkd.bytes.bytes, data->token_ctl_stat );
    SET_MSEC_CORE_CTX_RC_PK_PROT_AL_ENB(rec_pkd.bytes.bytes, data->prot_al_enb);
    SET_MSEC_CORE_CTX_RC_PK_CTXT_CONTROL(rec_pkd.bytes.bytes, data->ctxt_control);
    SET_MSEC_CORE_CTX_RC_PK_CTXT_STAT(rec_pkd.bytes.bytes, data->ctxt_stat);
    SET_MSEC_CORE_CTX_RC_PK_INTR_CTL_STAT(rec_pkd.bytes.bytes, data->intr_ctl_stat);
    SET_MSEC_CORE_CTX_RC_PK_SW_INTR(rec_pkd.bytes.bytes, data->sw_intr);
    SET_MSEC_CORE_CTX_RC_PK_SEQ_NUM_THRESH(rec_pkd.bytes.bytes, data->seq_num_thresh);
    SET_MSEC_CORE_CTX_RC_PK_TYPE(rec_pkd.bytes.bytes, data->type);
    SET_MSEC_CORE_CTX_RC_PK_VERSION(rec_pkd.bytes.bytes, data->version);

    addr = LEEDS_MACSEC_EGRESS_CORE_HOST0;

    /* Write the record back to registers */
    for(i = 0; i < sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }
  
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read the configuration registers from the MACsec core. 
 * 
 *  @param port  [I] -  The port to access. 
 *  @param data  [O] -  The configuration data read from the device. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ecc_rd(
        uint32                    port,
        uint32                    entry,
        leeds_macsec_core_ctxt_t* data)
{
    uint32 i;
    uint32 addr;
    uint16 reg_data;
    
    leeds_macsec_core_ctxt_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: egress core context\n");
#endif

    memset(&rec_pkd, 0, sizeof(rec_pkd));

    addr = LEEDS_MACSEC_EGRESS_CORE_HOST0;
  
    /* Read the record from registers */
    for(i = 0; i < sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }

    /* Now copy the record over */
    data->token_ctl_stat = GET_MSEC_CORE_CTX_RC_PK_TOKEN_CTRL_STAT(rec_pkd.bytes.bytes);
    data->prot_al_enb    = GET_MSEC_CORE_CTX_RC_PK_PROT_AL_ENB(rec_pkd.bytes.bytes);
    data->ctxt_control   = GET_MSEC_CORE_CTX_RC_PK_CTXT_CONTROL(rec_pkd.bytes.bytes);
    data->ctxt_stat      = GET_MSEC_CORE_CTX_RC_PK_CTXT_STAT(rec_pkd.bytes.bytes);
    data->intr_ctl_stat  = GET_MSEC_CORE_CTX_RC_PK_INTR_CTL_STAT(rec_pkd.bytes.bytes);
    data->sw_intr        = GET_MSEC_CORE_CTX_RC_PK_SW_INTR(rec_pkd.bytes.bytes);
    data->seq_num_thresh = GET_MSEC_CORE_CTX_RC_PK_SEQ_NUM_THRESH(rec_pkd.bytes.bytes);
    data->type           = GET_MSEC_CORE_CTX_RC_PK_TYPE(rec_pkd.bytes.bytes);
    data->version        = GET_MSEC_CORE_CTX_RC_PK_VERSION(rec_pkd.bytes.bytes);

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program all or part of the Ingress Core Context table 
 * in one operation. There really is only a single entry in the table but the
 * interface is kept the same for consistency with the other tables.
 *
 *  @param port         [I] -  The port number of the device to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of entries to write in the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ecc_tbl_wr(
        uint32                     port,
        uint32                     base,
        uint32                     num_entries,
        leeds_macsec_core_ctxt_t   entries[])
{
    uint32 i;
    cs_status rc = CS_OK;

    if((base + num_entries) > NUM_MACSEC_ECC_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_ecc_wr(port, i, &(entries[i]));

        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program an entry within the Egress Rules token table. 
 * 
 *  @param port         [I] -  The port number of the device to access. 
 *  @param entry        [I] -  The entry to program. 
 *  @param data         [I] -  The data to write into the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ert_wr(
        uint32                port,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    uint32 i;
    uint32 addr;
    
    leeds_macsec_token_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"WR: egress rules\n");
#endif

    if(entry > NUM_MACSEC_ERT_ENTRIES)
    {
      return CS_BOUNDS;
    }
       
    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));

    SET_MSEC_TKN_PK_TOKEN_TYPE(rec_pkd.bytes.bytes,  data->token_type);
    SET_MSEC_TKN_PK_PASS(rec_pkd.bytes.bytes,        data->pass);
    SET_MSEC_TKN_PK_DIRECTION(rec_pkd.bytes.bytes,   data->direction);
    SET_MSEC_TKN_PK_ES(rec_pkd.bytes.bytes,          data->es);
    SET_MSEC_TKN_PK_SC(rec_pkd.bytes.bytes,          data->sc);
    SET_MSEC_TKN_PK_SCB(rec_pkd.bytes.bytes,         data->scb);
    SET_MSEC_TKN_PK_TOO(rec_pkd.bytes.bytes,         data->too);
    SET_MSEC_TKN_PK_ECO(rec_pkd.bytes.bytes,         data->eco);
    SET_MSEC_TKN_PK_CO(rec_pkd.bytes.bytes,          data->co);
    SET_MSEC_TKN_PK_CID_UPDATE(rec_pkd.bytes.bytes,  data->cid_update);
    SET_MSEC_TKN_PK_OID_VALID(rec_pkd.bytes.bytes,   data->oid_valid);
    SET_MSEC_TKN_PK_LEN_VALID(rec_pkd.bytes.bytes,   data->len_valid);
    SET_MSEC_TKN_PK_INP_PKT_LEN(rec_pkd.bytes.bytes, data->inp_pkt_len);
    SET_MSEC_TKN_PK_CONTEXT_PTR(rec_pkd.bytes.bytes, data->context_ptr);
    SET_MSEC_TKN_PK_OUTPUT_ID(rec_pkd.bytes.bytes,   data->output_id);
    SET_MSEC_TKN_PK_EXTENDED_CO(rec_pkd.bytes.bytes, data->extended_co);

    addr = LEEDS_MACSEC_EGRESS_TOKEN_MEM0 + (entry * sizeof(rec_pkd.regs)/sizeof(uint16));
  
    /* Write the record back to registers */
    for(i = 0; i < sizeof(leeds_macsec_token_pkd_t)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i-1]));
      }
      else
      {
        leeds_reg_set(port, addr+i, htons(rec_pkd.regs.regs[i+1]));
      }
    }
  
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to read an entry from within the Egress Rules Token table. 
 * Entries are structured using the leeds_macsec_ert_entry_t structure. 
 *
 *  @param port         [I] -  The port number of the device to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of entries to store in the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ert_rd(
        uint32                port,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    uint32 addr;
    uint32 i;
    uint16 reg_data;
    
    /* Structures for unpacking the data and mask */
    leeds_macsec_token_pkd_t rec_pkd;

#ifdef LEEDS_MACSEC_DEBUG_FLAG
    dbg_dump(stdout,"RD: egress rules\n");
#endif

    if(entry > NUM_MACSEC_ERT_ENTRIES)
    {
        return CS_BOUNDS;
    }
  
    memset(rec_pkd.bytes.bytes, 0, sizeof(rec_pkd));
    
    addr = LEEDS_MACSEC_EGRESS_TOKEN_MEM0 + (entry * (sizeof(rec_pkd)/sizeof(uint16)));
    
    /* Read the packed entry from the h/w. */
    for(i = 0; i < sizeof(rec_pkd.regs)/sizeof(uint16); i++)
    {
      /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
      /* also, bits [15:0] written to addr+0, bits[31:16] to addr+1 */
      if (i & 1) 
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i-1] = ntohs(reg_data);
      }
      else
      {
        leeds_reg_get(port, addr+i, &reg_data);
        rec_pkd.regs.regs[i+1] = ntohs(reg_data);
      }
    }

    data->token_type  = GET_MSEC_TKN_PK_TOKEN_TYPE(rec_pkd.bytes.bytes);
    data->pass        = GET_MSEC_TKN_PK_PASS(rec_pkd.bytes.bytes);
    data->direction   = GET_MSEC_TKN_PK_DIRECTION(rec_pkd.bytes.bytes);
    data->es          = GET_MSEC_TKN_PK_ES(rec_pkd.bytes.bytes);
    data->sc          = GET_MSEC_TKN_PK_SC(rec_pkd.bytes.bytes);
    data->scb         = GET_MSEC_TKN_PK_SCB(rec_pkd.bytes.bytes);
    data->too         = GET_MSEC_TKN_PK_TOO(rec_pkd.bytes.bytes);
    data->eco         = GET_MSEC_TKN_PK_ECO(rec_pkd.bytes.bytes);
    data->co          = GET_MSEC_TKN_PK_CO(rec_pkd.bytes.bytes);
    data->cid_update  = GET_MSEC_TKN_PK_CID_UPDATE(rec_pkd.bytes.bytes);
    data->oid_valid   = GET_MSEC_TKN_PK_OID_VALID(rec_pkd.bytes.bytes);
    data->len_valid   = GET_MSEC_TKN_PK_LEN_VALID(rec_pkd.bytes.bytes);
    data->inp_pkt_len = GET_MSEC_TKN_PK_INP_PKT_LEN(rec_pkd.bytes.bytes);
    data->context_ptr = GET_MSEC_TKN_PK_CONTEXT_PTR(rec_pkd.bytes.bytes);
    data->output_id   = GET_MSEC_TKN_PK_OUTPUT_ID(rec_pkd.bytes.bytes);
    data->extended_co = GET_MSEC_TKN_PK_EXTENDED_CO(rec_pkd.bytes.bytes);

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to program all or part of the Egress Rules Token table in 
 * one operation. 
 *
 *  @param port         [I] -  The port number of the device to access. 
 *  @param base         [I] -  The first entry of the table to program. 
 *  @param num_entries  [I] -  The number of entries to program. 
 *  @param entries      [I] -  The array of entries to store in the table. 
 *
 *  @return                 -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_ert_tbl_wr(
        uint32                port,
        uint32                base,
        uint32                num_entries,
        leeds_macsec_token_t  entries[])
{
    uint32 i;
    cs_status rc = CS_OK;

    if((base + num_entries) > NUM_MACSEC_ERT_ENTRIES)
    {
        return CS_BOUNDS;
    }
    
    for(i = base; i < num_entries + base; i++)
    {
        cs_status cd = leeds_macsec_ert_wr(port, i, &(entries[i]));

        if(cd != CS_OK)
        {
            rc = cd;
            break;
        }
    }
    
    return rc;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Consistency Check Default Actions
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_cc_default_action(leeds_handle_t fd, uint32 port)
{
    uint16         reg_data;
    uint16         reg_data_miss_action;
    cs_status      status;
    int            i;
   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Consistency Check Default Actions\n");
    dbg_dump(fd, "+--------------+-------+------------------------------------------------------------\n");
    dbg_dump(fd, "|              |       | 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 \n");
    dbg_dump(fd, "|              | Entry | 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 \n");
    dbg_dump(fd, "|              +-------+------------------------------------------------------------\n");
    dbg_dump(fd, "| Frame Type   | Event | Action P=Passed-thru, D=Deleted\n");
    dbg_dump(fd, "+--------------+-------+------------------------------------------------------------\n");
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_CONTROL_FRAME, &reg_data);
    
    dbg_dump(fd, "| Controlled   |  Hit  | ");
    for (i=0; i<16; i++)
    {
      if ((reg_data >> i) & 1) 
      {
        dbg_dump(fd, "%s ", "P");
      }
      else
      {
        dbg_dump(fd, "%s ", "D");
      }
    }
    dbg_dump(fd, "\n|              +--------------------------------------------------------------------\n");
    dbg_dump(fd,   "|              |  Miss | ");

    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_MISS_ACTION, &reg_data_miss_action);

    if (0x2 & reg_data_miss_action)
    {
      dbg_dump(fd, "All Entries Passed-Thru\n");
    }
    else
    {
      dbg_dump(fd, "All Entries Deleted\n");
    }

    dbg_dump(fd, "+--------------+-------+------------------------------------------------------------\n");

    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CCTCAM_HIT_ACTION_NON_CONTROL_FRAME, &reg_data);
    
    dbg_dump(fd, "| Uncontrolled |  Hit  | ");
    for (i=0; i<16; i++)
    {
      if ((reg_data >> i) & 1) 
      {
        dbg_dump(fd, "%s ", "P");
      }
      else
      {
        dbg_dump(fd, "%s ", "D");
      }
    }
    dbg_dump(fd, "\n|              +--------------------------------------------------------------------\n");
    dbg_dump(fd,   "|              |  Miss | ");

    if (0x1 & reg_data_miss_action)
    {
      dbg_dump(fd, "All Entries Passed-Thru\n");
    }
    else
    {
      dbg_dump(fd, "All Entries Deleted\n");
    }

    dbg_dump(fd, "+--------------+-------+------------------------------------------------------------\n");

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Frame Validation Modes
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_frame_validation(leeds_handle_t fd, uint32 port)
{
    cs_status      status;
    leeds_macsec_frame_valid_token_rec_t token;
   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Frame Validation Modes\n");
    dbg_dump(fd, "+----------------------------+------------------------------------------------------\n");
    dbg_dump(fd, "| Frame Type                 | Mode\n");
    dbg_dump(fd, "+----------------------------+------------------------------------------------------\n");

    token.frame_type = e_leeds_macsec_ingress_controlled;
    /* read the HW */
    status = leeds_macsec_iefv_tok_rd(0, &token); 

    if (0x80000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Controlled Frame   | Strict\n");
    } 
    else if (0x40000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Controlled Frame   | Non-Strict\n");
    }
    else
    {
      dbg_dump(fd, "| Ingress Controlled Frame   | Not Configured\n");
    }

    token.frame_type = e_leeds_macsec_ingress_un_controlled;
    /* read the HW */
    status = leeds_macsec_iefv_tok_rd(0, &token); 

    if (0x80000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Uncontrolled Frame | Strict\n");
    } 
    else if (0x40000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Uncontrolled Frame | Non-strict\n");
    }
    else
    {
      dbg_dump(fd, "| Ingress UnControlled Frame | Not Configured\n");
    }

    token.frame_type = e_leeds_macsec_ingress_invalid_frame;
    /* read the HW */
    status = leeds_macsec_iefv_tok_rd(0, &token); 

    if (0x80000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Invalid Frame      | Strict\n");
    } 
    else if (0x40000000 == token.output_id)
    {
      dbg_dump(fd, "| Ingress Invalid Frame      | Non-Strict\n");
    }
    else
    {
      dbg_dump(fd, "| Ingress Invalid Frame      | Not Configured\n");
    }

    token.frame_type = e_leeds_macsec_egress_security_miss;
    /* read the HW */
    status = leeds_macsec_iefv_tok_rd(0, &token); 

    if (0x80000000 == token.output_id)
    {
      dbg_dump(fd, "| Egress Rule Miss           | Strict\n");
    } 
    else if (0x40000000 == token.output_id)
    {
      dbg_dump(fd, "| Egress Rule Miss           | Non-Strict\n");
    }
    else
    {
      dbg_dump(fd, "| Egress Rule Miss           | Not Configured\n");
    }

    dbg_dump(fd, "+---------+------------------+------------------------------------------------------\n");
    
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the CC Entry Valid Register
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_cc_entry_valid(leeds_handle_t fd, uint32 port)
{
    uint16    reg_data_15_0;
    cs_status status;
    int       i;
    uint32    bit;
   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Consistency Check Entry Valid Table\n");
    dbg_dump(fd, "+---------+-------------------------------------------------------------------------\n");
    dbg_dump(fd, "|         | 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1\n");
    dbg_dump(fd, "|  Entry  | 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5\n");
    dbg_dump(fd, "+---------+-------------------------------------------------------------------------\n");
    
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_CC_TCAM_Entry_Valid, &reg_data_15_0);
    
    dbg_dump(fd, "| Ingress | ");
    for (i=0; i<16; i++)
    {
      bit = (reg_data_15_0 >> i) & 1; 
      dbg_dump(fd, "%d ",bit);
    }

    dbg_dump(fd, "\n+---------+-------------------------------------------------------------------------\n");
    
    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the CAM Entry Valid Register
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_cam_entry_valid(leeds_handle_t fd, uint32 port)
{
    uint16    reg_data_15_0;
    uint16    reg_data_31_16;
    cs_status status;
    int       i;
    uint32    bit;
   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| CAM Entry Valid Table\n");
    dbg_dump(fd, "+---------+-------------------------------------------------------------------------\n");
    dbg_dump(fd, "|         | 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 2 2 2 2 2 2 2 2 2 2 3 3 \n");
    dbg_dump(fd, "|  Entry  | 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 \n");
    dbg_dump(fd, "+---------+-------------------------------------------------------------------------\n");
    
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_15_0, &reg_data_15_0);
    status = leeds_reg_get(port, LEEDS_MACSEC_INGRESS_TCAM_Entry_Valid_31_16, &reg_data_31_16);
    
    dbg_dump(fd, "| Ingress | ");
    for (i=0; i<16; i++)
    {
      bit = (reg_data_15_0 >> i) & 1; 
      dbg_dump(fd, "%d ",bit);
    }
    for (i=0; i<16; i++)
    {
      bit = (reg_data_31_16 >> i) & 1; 
      dbg_dump(fd, "%d ",bit);
    }
    status = leeds_reg_get(port, LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_15_0, &reg_data_15_0);
    status = leeds_reg_get(port, LEEDS_MACSEC_EGRESS_TCAM_Entry_Valid_31_16, &reg_data_31_16);
    
    dbg_dump(fd, "\n|  Egress | ");
    for (i=0; i<16; i++)
    {
      bit = (reg_data_15_0 >> i) & 1; 
      dbg_dump(fd, "%d ",bit);
    }
    for (i=0; i<16; i++)
    {
      bit = (reg_data_31_16 >> i) & 1; 
      dbg_dump(fd, "%d ",bit);
    }
    
    dbg_dump(fd, "\n+---------+-------------------------------------------------------------------------\n");
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Security Association Map for all CAM entries to the specified file 
 * handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_sa_map(leeds_handle_t fd, uint32 port)
{
    uint32 i_addr, e_addr;
    uint16 reg_data;
    uint32 i;
    leeds_macsec_sa_map_pkd_t i_sam_pkd, e_sam_pkd;

   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Security Association Map Table\n");
    dbg_dump(fd, "+---------------------------+-------------------------------------------------------\n");
    dbg_dump(fd, "|         Ingress           |          Egress\n");
    dbg_dump(fd, "+------+------+-------------+------+------+-----------------------------------------\n");
    dbg_dump(fd, "| CAM# | CTX# | State       | CAM# | CTX# | State\n");
    dbg_dump(fd, "+------+------+-------------+------+------+-----------------------------------------\n");
    
    memset(i_sam_pkd.bytes.bytes, 0, sizeof(i_sam_pkd));
    memset(e_sam_pkd.bytes.bytes, 0, sizeof(e_sam_pkd));

    i_addr = LEEDS_MACSEC_INGRESS_STCAM_SA_MAP9;
    e_addr = LEEDS_MACSEC_EGRESS_STCAM_SA_MAP9;

    for(i = 0; i < sizeof(i_sam_pkd.regs)/sizeof(uint16); i++)
    {
        leeds_reg_get(port, i_addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        i_sam_pkd.regs.regs[i] = ntohs(reg_data);

        leeds_reg_get(port, e_addr+i, &reg_data);
        /* note: use htons/ntohs when memory storage is in left justified bit vector (packed) */
        e_sam_pkd.regs.regs[i] = ntohs(reg_data);
    }

    for(i = 0; i < NUM_MACSEC_IPR_CAM_ENTRIES; i++)
    {
      switch(i)
      {
        case 0 : reg_data = GET_MSEC_SA_MAP_TCAM_00(i_sam_pkd.bytes.bytes); break;
        case 1 : reg_data = GET_MSEC_SA_MAP_TCAM_01(i_sam_pkd.bytes.bytes); break;
        case 2 : reg_data = GET_MSEC_SA_MAP_TCAM_02(i_sam_pkd.bytes.bytes); break;
        case 3 : reg_data = GET_MSEC_SA_MAP_TCAM_03(i_sam_pkd.bytes.bytes); break;
        case 4 : reg_data = GET_MSEC_SA_MAP_TCAM_04(i_sam_pkd.bytes.bytes); break;
        case 5 : reg_data = GET_MSEC_SA_MAP_TCAM_05(i_sam_pkd.bytes.bytes); break;
        case 6 : reg_data = GET_MSEC_SA_MAP_TCAM_06(i_sam_pkd.bytes.bytes); break;
        case 7 : reg_data = GET_MSEC_SA_MAP_TCAM_07(i_sam_pkd.bytes.bytes); break;
        case 8 : reg_data = GET_MSEC_SA_MAP_TCAM_08(i_sam_pkd.bytes.bytes); break;
        case 9 : reg_data = GET_MSEC_SA_MAP_TCAM_09(i_sam_pkd.bytes.bytes); break;
        case 10: reg_data = GET_MSEC_SA_MAP_TCAM_10(i_sam_pkd.bytes.bytes); break;
        case 11: reg_data = GET_MSEC_SA_MAP_TCAM_11(i_sam_pkd.bytes.bytes); break;
        case 12: reg_data = GET_MSEC_SA_MAP_TCAM_12(i_sam_pkd.bytes.bytes); break;
        case 13: reg_data = GET_MSEC_SA_MAP_TCAM_13(i_sam_pkd.bytes.bytes); break;
        case 14: reg_data = GET_MSEC_SA_MAP_TCAM_14(i_sam_pkd.bytes.bytes); break;
        case 15: reg_data = GET_MSEC_SA_MAP_TCAM_15(i_sam_pkd.bytes.bytes); break;
        case 16: reg_data = GET_MSEC_SA_MAP_TCAM_16(i_sam_pkd.bytes.bytes); break;
        case 17: reg_data = GET_MSEC_SA_MAP_TCAM_17(i_sam_pkd.bytes.bytes); break;
        case 18: reg_data = GET_MSEC_SA_MAP_TCAM_18(i_sam_pkd.bytes.bytes); break;
        case 19: reg_data = GET_MSEC_SA_MAP_TCAM_19(i_sam_pkd.bytes.bytes); break;
        case 20: reg_data = GET_MSEC_SA_MAP_TCAM_20(i_sam_pkd.bytes.bytes); break;
        case 21: reg_data = GET_MSEC_SA_MAP_TCAM_21(i_sam_pkd.bytes.bytes); break;
        case 22: reg_data = GET_MSEC_SA_MAP_TCAM_22(i_sam_pkd.bytes.bytes); break;
        case 23: reg_data = GET_MSEC_SA_MAP_TCAM_23(i_sam_pkd.bytes.bytes); break;
        case 24: reg_data = GET_MSEC_SA_MAP_TCAM_24(i_sam_pkd.bytes.bytes); break;
        case 25: reg_data = GET_MSEC_SA_MAP_TCAM_25(i_sam_pkd.bytes.bytes); break;
        case 26: reg_data = GET_MSEC_SA_MAP_TCAM_26(i_sam_pkd.bytes.bytes); break;
        case 27: reg_data = GET_MSEC_SA_MAP_TCAM_27(i_sam_pkd.bytes.bytes); break;
        case 28: reg_data = GET_MSEC_SA_MAP_TCAM_28(i_sam_pkd.bytes.bytes); break;
        case 29: reg_data = GET_MSEC_SA_MAP_TCAM_29(i_sam_pkd.bytes.bytes); break;
        case 30: reg_data = GET_MSEC_SA_MAP_TCAM_30(i_sam_pkd.bytes.bytes); break;
        case 31: reg_data = GET_MSEC_SA_MAP_TCAM_31(i_sam_pkd.bytes.bytes); break;
        default:
          break;
  
      }
      dbg_dump(fd, "|  %02d  |  %02d  |", i, (reg_data & 0xf));
      if (reg_data & 0x10)
      {
        dbg_dump(fd, " Enabled     ");
      }
      else
      {
        dbg_dump(fd, " Disabled    ");
      }

      switch(i)
      {
        case 0 : reg_data = GET_MSEC_SA_MAP_TCAM_00(e_sam_pkd.bytes.bytes); break;
        case 1 : reg_data = GET_MSEC_SA_MAP_TCAM_01(e_sam_pkd.bytes.bytes); break;
        case 2 : reg_data = GET_MSEC_SA_MAP_TCAM_02(e_sam_pkd.bytes.bytes); break;
        case 3 : reg_data = GET_MSEC_SA_MAP_TCAM_03(e_sam_pkd.bytes.bytes); break;
        case 4 : reg_data = GET_MSEC_SA_MAP_TCAM_04(e_sam_pkd.bytes.bytes); break;
        case 5 : reg_data = GET_MSEC_SA_MAP_TCAM_05(e_sam_pkd.bytes.bytes); break;
        case 6 : reg_data = GET_MSEC_SA_MAP_TCAM_06(e_sam_pkd.bytes.bytes); break;
        case 7 : reg_data = GET_MSEC_SA_MAP_TCAM_07(e_sam_pkd.bytes.bytes); break;
        case 8 : reg_data = GET_MSEC_SA_MAP_TCAM_08(e_sam_pkd.bytes.bytes); break;
        case 9 : reg_data = GET_MSEC_SA_MAP_TCAM_09(e_sam_pkd.bytes.bytes); break;
        case 10: reg_data = GET_MSEC_SA_MAP_TCAM_10(e_sam_pkd.bytes.bytes); break;
        case 11: reg_data = GET_MSEC_SA_MAP_TCAM_11(e_sam_pkd.bytes.bytes); break;
        case 12: reg_data = GET_MSEC_SA_MAP_TCAM_12(e_sam_pkd.bytes.bytes); break;
        case 13: reg_data = GET_MSEC_SA_MAP_TCAM_13(e_sam_pkd.bytes.bytes); break;
        case 14: reg_data = GET_MSEC_SA_MAP_TCAM_14(e_sam_pkd.bytes.bytes); break;
        case 15: reg_data = GET_MSEC_SA_MAP_TCAM_15(e_sam_pkd.bytes.bytes); break;
        case 16: reg_data = GET_MSEC_SA_MAP_TCAM_16(e_sam_pkd.bytes.bytes); break;
        case 17: reg_data = GET_MSEC_SA_MAP_TCAM_17(e_sam_pkd.bytes.bytes); break;
        case 18: reg_data = GET_MSEC_SA_MAP_TCAM_18(e_sam_pkd.bytes.bytes); break;
        case 19: reg_data = GET_MSEC_SA_MAP_TCAM_19(e_sam_pkd.bytes.bytes); break;
        case 20: reg_data = GET_MSEC_SA_MAP_TCAM_20(e_sam_pkd.bytes.bytes); break;
        case 21: reg_data = GET_MSEC_SA_MAP_TCAM_21(e_sam_pkd.bytes.bytes); break;
        case 22: reg_data = GET_MSEC_SA_MAP_TCAM_22(e_sam_pkd.bytes.bytes); break;
        case 23: reg_data = GET_MSEC_SA_MAP_TCAM_23(e_sam_pkd.bytes.bytes); break;
        case 24: reg_data = GET_MSEC_SA_MAP_TCAM_24(e_sam_pkd.bytes.bytes); break;
        case 25: reg_data = GET_MSEC_SA_MAP_TCAM_25(e_sam_pkd.bytes.bytes); break;
        case 26: reg_data = GET_MSEC_SA_MAP_TCAM_26(e_sam_pkd.bytes.bytes); break;
        case 27: reg_data = GET_MSEC_SA_MAP_TCAM_27(e_sam_pkd.bytes.bytes); break;
        case 28: reg_data = GET_MSEC_SA_MAP_TCAM_28(e_sam_pkd.bytes.bytes); break;
        case 29: reg_data = GET_MSEC_SA_MAP_TCAM_29(e_sam_pkd.bytes.bytes); break;
        case 30: reg_data = GET_MSEC_SA_MAP_TCAM_30(e_sam_pkd.bytes.bytes); break;
        case 31: reg_data = GET_MSEC_SA_MAP_TCAM_31(e_sam_pkd.bytes.bytes); break;
        default:
          break;
  
      }
      dbg_dump(fd, "|  %02d  |  %02d  |", i, (reg_data & 0xf));
      if (reg_data & 0x10)
      {
        dbg_dump(fd, " Enabled\n");
      }
      else
      {
        dbg_dump(fd, " Disabled\n");
      }

    }
    
    dbg_dump(fd, "+------+------+-------------+------+------+-----------------------------------------\n");
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps memory low addresses to high
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_all_pkd(leeds_handle_t fd, uint32 port)
{
    uint32 addr;
    uint32 base_addr;
    uint16 reg_data;
    uint32 i, j, k;
    uint32 size;
    uint32 pkd_num;
    uint32 entries;

    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Raw Memory bit dump, starts at lowest address of record, MSbit left\n");
    
    for (pkd_num=0; pkd_num < 18; pkd_num++)
    {
      dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
      switch (pkd_num)
      {
        case 0  :
          dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
          dbg_dump(fd, "\n                                    INGRESS\n\n");
          dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
          base_addr = LEEDS_MACSEC_INGRESS_CORE_HOST0;
          size = sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Ingress Core Context\n");
          break;

        case 1  :
          base_addr = LEEDS_MACSEC_INGRESS_TCAM0;
          size = sizeof(leeds_macsec_ipr_cam_entry_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_IPR_CAM_ENTRIES;
          dbg_dump(fd, "Ingress Parser CAM\n");
          break;

        case 2  :
          base_addr = LEEDS_MACSEC_INGRESS_TCAM_ENTRY_0_MASK;
          size = sizeof(leeds_macsec_ipr_cam_mask_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_IPR_CAM_ENTRIES;
          dbg_dump(fd, "Ingress Parser CAM Mask\n");
          break;

        case 3  :
          base_addr = LEEDS_MACSEC_INGRESS_TOKEN_MEM0;
          size = sizeof(leeds_macsec_token_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_ERT_ENTRIES;
          dbg_dump(fd, "Ingress Token Rules\n");
          break;

        case 4  :
          base_addr = LEEDS_MACSEC_INGRESS_CTX_MEM0;
          size = sizeof(leeds_macsec_ctxt_rec_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_ICT_ENTRIES;
          dbg_dump(fd, "Ingress Context\n");
          break;

        case 5  :
          base_addr = LEEDS_MACSEC_INGRESS_CC_TCAM0;
          size = sizeof(leeds_macsec_chk_cam_entry_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_CHK_CAM_ENTRIES;
          dbg_dump(fd, "Ingress Consistency Check CAM\n");
          break;

        case 6  :
          base_addr = LEEDS_MACSEC_INGRESS_CC_TCAM_ENTRY_0_MASK;
          size = sizeof(leeds_macsec_chk_cam_mask_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_CHK_CAM_ENTRIES;
          dbg_dump(fd, "Ingress Consistency Check CAM Mask\n");
          break;

        case 7  :
          base_addr = LEEDS_MACSEC_INGRESS_CONTROLLED_FRAME_STCAM_MISS_TOKEN5;
          size = sizeof(leeds_macsec_frame_valid_token_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Ingress Controlled Frame Miss Token\n");
          break;

        case 8  :
          base_addr = LEEDS_MACSEC_INGRESS_UNCONTROLLED_FRAME_STCAM_MISS_TOKEN5;
          size = sizeof(leeds_macsec_frame_valid_token_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Ingress Uncontrolled Frame Miss Token\n");
          break;

        case 9  :
          base_addr = LEEDS_MACSEC_INGRESS_STCAM_INVALID_FRAME_TOKEN5;
          size = sizeof(leeds_macsec_frame_valid_token_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Ingress Invalid Frame Token\n");
          break;

        case 10 :
          base_addr = LEEDS_MACSEC_INGRESS_STCAM_SA_MAP9;
          size = sizeof(leeds_macsec_sa_map_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Ingress Security Association Map\n");
          break;

        case 11 :
          dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
          dbg_dump(fd, "\n                                    EGRESS\n\n");
          dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
          base_addr = LEEDS_MACSEC_EGRESS_CORE_HOST0;
          size = sizeof(leeds_macsec_core_ctxt_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Egress Core Context\n");
          break;

        case 12 :
          base_addr = LEEDS_MACSEC_EGRESS_TCAM0;
          size = sizeof(leeds_macsec_epr_cam_entry_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_IPR_CAM_ENTRIES;
          dbg_dump(fd, "Egress Parser CAM\n");
          break;

        case 13 :
          base_addr = LEEDS_MACSEC_EGRESS_TCAM_ENTRY_0_MASK;
          size = sizeof(leeds_macsec_ipr_cam_mask_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_IPR_CAM_ENTRIES;
          dbg_dump(fd, "Egress Parser CAM Mask\n");
          break;

        case 14 :
          base_addr = LEEDS_MACSEC_EGRESS_TOKEN_MEM0;
          size = sizeof(leeds_macsec_token_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_ERT_ENTRIES;
          dbg_dump(fd, "Egress Token Rules\n");
          break;

        case 15 :
          base_addr = LEEDS_MACSEC_EGRESS_CTX_MEM0;
          size = sizeof(leeds_macsec_ctxt_rec_pkd_t)/sizeof(uint16);
          entries = NUM_MACSEC_ICT_ENTRIES;
          dbg_dump(fd, "Egress Context\n");
          break;

        case 16 :
          base_addr = LEEDS_MACSEC_EGRESS_STCAM_MISS_TOKEN5;
          size = sizeof(leeds_macsec_frame_valid_token_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Egress Miss Token\n");
          break;

        case 17 :
          base_addr = LEEDS_MACSEC_EGRESS_STCAM_SA_MAP9;
          size = sizeof(leeds_macsec_sa_map_pkd_t)/sizeof(uint16);
          entries = 1;
          dbg_dump(fd, "Egress Security Association Map\n");
          break;

        default:
          base_addr = 0;
          addr = 0;
          size = 0;
          entries = 0;
          break;
      }


      /*
      Note: it ain't pretty, but it works
      */
      for (k=0; k < entries; k++)
      {
        if (1 < entries)
        {
          addr = base_addr + (k * size);
          dbg_dump(fd, "Entry:   %d\n", k);
        }
        else
        {
          addr = base_addr;
        }

        dbg_dump(fd, "Address: ");
        for(i = 0; i < size; i++)
        {
          dbg_dump(fd, "0x%04x ", addr+i );
          if (0 == ((i+1) % 8))
          {
            if (i < (size-1))
            {
              dbg_dump(fd, "\n         ");
            }
          }
        }
     
        dbg_dump(fd, "\n");
        dbg_dump(fd, "Words:   ");
        for(i = 0; i < size; i++)
        {
          leeds_reg_get(port, addr+i, &reg_data);
          dbg_dump(fd, "0x%04x ", reg_data );
          if (0 == ((i+1) % 8))
          {
            if (i < (size-1))
            {
              dbg_dump(fd, "\n         ");
            }
          }
        }

        dbg_dump(fd, "\n");
        dbg_dump(fd, "Binary:  ");
        for(i = 0; i < size; i++)
        {
          leeds_reg_get(port, addr+i, &reg_data);
     
          for (j=16; j>0; j--)
          {
            if (reg_data & (1 << (j-1)))
            {
              dbg_dump(fd, "1");
            }
            else
            {
              dbg_dump(fd, "0");
            }
            if (0 == ((j-1) % 8)) 
            {
              dbg_dump(fd, " ");
            }
          }
          if (0 == ((i+1) % 4))
          {
            if (i < (size-1))
            {
              dbg_dump(fd, "\n         ");
            }
          }
        } 
        dbg_dump(fd, "\n");
      }
    }
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n");
    
    return CS_OK;
}



/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Ingress Classification Parser TCAM for all ports to the specified file 
 * handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_ipr_cam(leeds_handle_t fd, uint32 port)
{
    int i = 0;
   
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Parser CAM Table\n");
    dbg_dump(fd, "+--+--+----------------+-----------------+-----------------+--------+------+--------\n");
    dbg_dump(fd, "| #|TP| SCI            | DA              | SA              | TCI_AN | ET   | FE\n");
    dbg_dump(fd, "+--+--+----------------+-----------------+-----------------+--------+------+--------\n");
    
    for(i = 0; i < NUM_MACSEC_IPR_CAM_ENTRIES; i++)
    {
        leeds_macsec_ipr_cam_entry_t cam;
        leeds_macsec_ipr_cam_mask_t  mask;
    
        /* Read the entry from the h/w */
        leeds_macsec_ipr_cam_rd(port, i, &cam, &mask);
    
        /* Dump the contents of the entry */
        leeds_macsec_print_ipr_cam_ent(fd, i, &cam, &mask);
    }
    
    dbg_dump(fd, "+--+--+----------------+-----------------+-----------------+--------+------+--------\n");
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Ingress Context Table for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_ict(leeds_handle_t fd, uint32 port)
{
    uint32 i;
    
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Context Table\n");
    dbg_dump(fd, "+--+--+----------------+--------+--------+------------------------------------------\n"); 
    dbg_dump(fd, "| #|W0| IV1    IV0     | SQ# MSK| SQ#    | HASH\n");
    dbg_dump(fd, "|  |W1| KEY                              | CTXT ID       | CTRL WORD\n");
    dbg_dump(fd, "|  |W2| CI| SM| ST| AN| AA| DT| CA| KY| ER| IF| US| CL| V2| V1| V0| PO| TP\n");
    dbg_dump(fd, "|--+--+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+-------------\n");   

    for(i = 0; i < NUM_MACSEC_ICT_ENTRIES; i++)
    {
        leeds_macsec_ctxt_rec_t data;
        
        /* Read the entry from the h/w */
        leeds_macsec_ict_rd(port, i, &data);
    
        /* Dump the contents of the entry */
        leeds_macsec_print_ict_ent(fd, i, &data);
/*      dbg_dump(fd, "+--+--+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+-------------\n"); */
    }
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Ingress Core Configuration table for all ports to the specified handle. 
 * 
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_icc(leeds_handle_t fd, uint32 port)
{
    int i = 0;

    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Core Context Table\n");
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");
    dbg_dump(fd, "| #| TKN ST | P/A EN | CTX CT | CTX ST |INT C/ST|  SWINT | SQ# TH |  TYPE  |   VER \n");
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");

    for(i = 0; i < NUM_MACSEC_ICC_ENTRIES; i++)
    {
        leeds_macsec_core_ctxt_t ctxt;
      
        /* First read the core configuration context */
        leeds_macsec_icc_rd(port, i, &ctxt);
      
        /* Now display the context */
        leeds_macsec_print_icc_ent(fd, i, &ctxt);
    }
    
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Ingress Rules Token Table for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_irt(leeds_handle_t fd, uint32 port)
{
    int i = 0;

    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Token Rules Table\n");
    dbg_dump(fd, "+--+---+--+--+--+--+--+----+---+--+---+--+--+------+---------+--------+-------------\n");
    dbg_dump(fd, "| #|TYP|PS|DR|ES|SC|SCB|TOO|ECO|CO|CID|OV|LV|  LEN | CTX_PTR | OUT_ID | EXT_CO   \n");
    dbg_dump(fd, "+--+---+--+--+--+--+---+---+---+--+---+--+--+------+---------+--------+-------------\n");

    for(i = 0; i < NUM_MACSEC_IRT_ENTRIES; i++)
    {
        leeds_macsec_token_t token;
      
        /* First read the rule context */
        leeds_macsec_irt_rd(port, i, &token);
      
        /* Now display the context */
        leeds_macsec_print_irt_ent(fd, i, &token);
    }
    
    dbg_dump(fd, "+--+---+--+--+--+--+---+---+---+--+---+--+--+------+---------+--------+-------------\n");

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Ingress Consistency Check TCAM for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 * 
 */
cs_status leeds_macsec_show_port_table_chk_cam(leeds_handle_t fd, uint32 port)
{
    /* FUNCTION PSEUDOCODE: */
    int i = 0;
    
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Ingress Consistency Check CAM Table\n");
    dbg_dump(fd, "+--+--+------+----+----+------+----+------------------------------------------------\n"); 
    dbg_dump(fd, "| #|TP| ET   | EV | TG | VLAN | SH | SAI\n");
    dbg_dump(fd, "+--+--+------+----+----+------+----+------------------------------------------------\n"); 

    for(i = 0; i < NUM_MACSEC_CHK_CAM_ENTRIES; i++)
    {
        leeds_macsec_chk_cam_entry_t cam;
        leeds_macsec_chk_cam_mask_t  mask;
        
        /* Read the entry from the h/w */
        leeds_macsec_chk_cam_rd(port, i, &cam, &mask);
        
        /* Dump the contents of the entry */
        leeds_macsec_print_chk_cam_ent(fd, i, &cam, &mask);
    }
    
    dbg_dump(fd, "+--+--+------+----+----+------+----+------------------------------------------------\n"); 
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Egress Classification Parser TCAM for all ports to the specified file 
 * handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_epr_cam(leeds_handle_t fd, uint32 port)
{
    int i = 0;
    
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Egress Parser CAM Table\n");
    dbg_dump(fd, "+--+--+------+-------+-----------------+--------------------------------------------\n");
    dbg_dump(fd, "| #|TP| VLAN | ETYPE | DA              | SA\n");
    dbg_dump(fd, "+--+--+------+-------+-----------------+--------------------------------------------\n");
    
    for(i = 0; i < NUM_MACSEC_EPR_CAM_ENTRIES; i++)
    {
        leeds_macsec_epr_cam_entry_t cam;
        leeds_macsec_epr_cam_mask_t  mask;
    
        /* Read the entry from the h/w */
        leeds_macsec_epr_cam_rd(port, i, &cam, &mask);
    
        /* Dump the contents of the entry */
        leeds_macsec_print_epr_cam_ent(fd, i, &cam, &mask);
    }
    
    dbg_dump(fd, "+--+--+---------+------+-------+-----------------+----------------------------------\n");
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Egress Context Table for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_ect(leeds_handle_t fd, uint32 port)
{
    uint32 i;
    
    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Egress Context Table\n");
    dbg_dump(fd, "+--+--+----------------+--------+--------+------------------------------------------\n"); 
    dbg_dump(fd, "| #|W0| IV1    IV0     | SQ# MSK| SQ#    | HASH\n");
    dbg_dump(fd, "|  |W1| KEY                              | CTXT ID       | CTRL WORD\n");
    dbg_dump(fd, "|  |W2| CI| SM| ST| AN| AA| DT| CA| KY| ER| IF| US| CL| V2| V1| V0| PO| TP\n");
    dbg_dump(fd, "|--+--+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+-------------\n"); 
    
    for(i = 0; i < NUM_MACSEC_ECT_ENTRIES; i++)
    {
        leeds_macsec_ctxt_rec_t data;
        
        /* Read the entry from the h/w */
        leeds_macsec_ect_rd(port, i, &data);
    
        /* Dump the contents of the entry */
        leeds_macsec_print_ect_ent(fd, i, &data);
        dbg_dump(fd, "+--+--+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+-------------\n"); 
    }
    
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Egress Core Configuration table for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 * 
 */
cs_status leeds_macsec_show_port_table_ecc(leeds_handle_t fd, uint32 port)
{
    int i = 0;

    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Egress Core Context Table\n");
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");
    dbg_dump(fd, "| #| TKN ST | P/A EN | CTX CT | CTX ST |INT C/ST|  SWINT | SQ# TH |  TYPE  |   VER \n");
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");

    for(i = 0; i < NUM_MACSEC_ECC_ENTRIES; i++)
    {
        leeds_macsec_core_ctxt_t ctxt;
      
        /* First read the core configuration context */
        leeds_macsec_ecc_rd(port, i, &ctxt);
      
        /* Now display the context */
        leeds_macsec_print_ecc_ent(fd, i, &ctxt);
    }
    
    dbg_dump(fd, "+--+--------+--------+--------+--------+--------+--------+--------+--------+--------\n");

    return CS_OK;
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * Dumps the Egress Rules Token Table for all ports to the specified handle. 
 *
 *  @param fd    [I] -  The file handle to dump output to. 
 *  @param port  [I] -  The port number of the device to access. 
 *
 *  @return        -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_show_port_table_ert(leeds_handle_t fd, uint32 port)
{
    int i = 0;

    DEBUG_TABLE_HEADER(fd);
    dbg_dump(fd, "+-----------------------------------------------------------------------------------\n"); 
    dbg_dump(fd, "| Egress Token Rules Table\n");
    dbg_dump(fd, "+--+---+--+--+--+--+--+----+---+--+---+--+--+------+---------+--------+-------------\n");
    dbg_dump(fd, "| #|TYP|PS|DR|ES|SC|SCB|TOO|ECO|CO|CID|OV|LV|  LEN | CTX_PTR | OUT_ID | EXT_CO   \n");
    dbg_dump(fd, "+--+---+--+--+--+--+---+---+---+--+---+--+--+------+---------+--------+-------------\n");

    for(i = 0; i < NUM_MACSEC_ERT_ENTRIES; i++)
    {
        leeds_macsec_token_t token;
      
        /* First read the rule context */
        leeds_macsec_ert_rd(port, i, &token);
      
        /* Now display the context */
        leeds_macsec_print_ert_ent(fd, i, &token);
    }
    
    dbg_dump(fd, "+--+---+--+--+--+--+---+---+---+--+---+--+--+------+---------+--------+-------------\n");

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display a single entry in the Ingress Parser TCAM. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The number of the entry being displayed. 
 *  @param cam    [I] -  The contents of the CAM entry. 
 *  @param mask   [I] -  The contents of the mask associated with the CAM entry. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_ipr_cam_ent(
        leeds_handle_t                fd,
        uint32                        entry,
        leeds_macsec_ipr_cam_entry_t* cam,
        leeds_macsec_ipr_cam_mask_t*  mask)
{
    char da[24];
    char sa[24];
  
    fmt_mac_addr(da, cam->da);
    fmt_mac_addr(sa, cam->sa);
  
    dbg_dump(fd, "|%02d|CM|%016" FMT_LLX "x|%16s|%16s|%08x| %04x | %02x\n",
         entry, cam->sci, da, sa, cam->tci_an, cam->et, cam->fe);
    dbg_dump(fd, "|__| M|%16x| %16x| %16x|%8x| %4x | %2x\n",
         mask->sci, mask->da, mask->sa, mask->tci_an, mask->et, mask->fe);
  
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display a single entry in the Ingress Context table. 
 * 
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The entry being displayed. 
 *  @param data   [I] -  The context record data to display. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_ict_ent(
        leeds_handle_t           fd,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    char buffer[40];
    leeds_macsec_ctxt_ctrl_t     ctxt_ctrl;

    dbg_dump(fd, "|%02d|W0|%08x%08x|%08x|%08x| %32s\n",
         entry, data->iv1, data->iv0, data->seq_num_mask,
         data->seq_num,
         fmt_key(buffer, data->hkey));
    dbg_dump(fd, "|  |W1| %32s | %-13x | %-16x\n",
         fmt_key(buffer, data->akey), data->ctxt_id, data->ctrl_word);

    ctxt_ctrl.regs.reg = data->ctrl_word;

    dbg_dump(fd, "|__|W2| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x\n",
         ctxt_ctrl.fields.ctxt_id,
         ctxt_ctrl.fields.seq_mask,
         ctxt_ctrl.fields.seq_type,
         ctxt_ctrl.fields.an,
         ctxt_ctrl.fields.authent_al,
         ctxt_ctrl.fields.digest_type,
         ctxt_ctrl.fields.crypto_al,
         ctxt_ctrl.fields.key,
         ctxt_ctrl.fields.encrypt_auth,
         ctxt_ctrl.fields.iv_format,
         ctxt_ctrl.fields.up_seq_num,
         ctxt_ctrl.fields.ct_len,
         ctxt_ctrl.fields.iv03,
         ctxt_ctrl.fields.iv02,
         ctxt_ctrl.fields.iv01,
         ctxt_ctrl.fields.pack_b_op,
         ctxt_ctrl.fields.top );

      return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display an entry in the the Ingress Core Configuration 
 * table. In reality there is only one entry but it is provided to keep it similar 
 * to the other print methods. 
 *
 *  @param fd    [I] -  The file handle to write to. 
 *  @param data  [I] -  The core configuration entry to display. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_icc_ent(
        leeds_handle_t            fd,
        uint32                    entry,
        leeds_macsec_core_ctxt_t* data)
{
    dbg_dump(fd, "| %d|%08x|%08x|%08x|%08x|%08x|%08x|%08x|%08x|%08x\n",
                 entry,
                 data->token_ctl_stat, data->prot_al_enb, data->ctxt_control,
                 data->ctxt_stat, data->intr_ctl_stat, data->sw_intr,
                 data->seq_num_thresh, data->type, data->version);
   
    return CS_OK; 
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display an entry in the Ingress Rules Token table. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The entry to display. 
 *  @param data   [I] -  The data associated with the rule to display. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_irt_ent(
        leeds_handle_t        fd,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    dbg_dump(fd, "|%02d| %02x|%02x|%02x|%02x|%02x| %02x| %02x| %02x|%02x| %02x|%02x|%02x|%06x| %08x|%08x| %08x\n",
                 entry,
                 data->token_type, data->pass, data->direction, data->es,
                 data->sc, data->scb, data->too, data->eco, data->co,
                 data->cid_update, data->oid_valid, data->len_valid,
                 data->inp_pkt_len, data->context_ptr, data->output_id,
                 data->extended_co);
                 
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is used to dump the contents of an Ingress Consistency Check TCAM 
 * entry. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The TCAM entry being displayed. 
 *  @param cam    [I] -  The data associated with the TCAM entry. 
 *  @param mask   [I] -  The mask associated with the TCAM entry. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_chk_cam_ent(
            leeds_handle_t                fd,
            uint32                        entry,
            leeds_macsec_chk_cam_entry_t* cam,
            leeds_macsec_chk_cam_mask_t*  mask)
{
    dbg_dump(fd, "|%02d|CM| %04x | %02x | %02x | %04x | %02x | %02x\n",
                 entry, cam->et, cam->ev, cam->tg, cam->vlan, cam->sh, cam->sai); 
    dbg_dump(fd, "|__|M | %04x | %02x | %02x | %04x | %02x | %02x\n",
                 mask->et, mask->ev, mask->tg, mask->vlan, mask->sh, mask->sai); 
   
    return CS_OK; 
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display a single entry in the Egress Parser TCAM. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The entry number being displayed. 
 *  @param data   [I] -  The TCAM entry. 
 *  @param mask   [I] -  The mask associated with the entry. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_epr_cam_ent(
        leeds_handle_t                fd,
        uint32                        entry,
        leeds_macsec_epr_cam_entry_t* cam,
        leeds_macsec_epr_cam_mask_t*  mask)
{
    char da[24];
    char sa[24];

    fmt_mac_addr(da, cam->da);
    fmt_mac_addr(sa, cam->sa);
  
    dbg_dump(fd, "|%02d|CM| %04x |  %04x |%17s|%17s\n",
         entry, cam->vlan, cam->et, da, sa);
    dbg_dump(fd, "|  | M| %4x |  %4x |%17x|%17x\n",
         mask->vlan, mask->et, mask->da, mask->sa);
  
    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display a single entry in the Egress Context Table. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The entry number to display. 
 *  @param data   [I] -  The data associated with the entry. 
 *
 *  @param return     -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_ect_ent(
        leeds_handle_t           fd,
        uint32                   entry,
        leeds_macsec_ctxt_rec_t* data)
{
    char buffer[40];
    leeds_macsec_ctxt_ctrl_t     ctxt_ctrl;


    dbg_dump(fd, "|%02d|W0|%08x%08x|%08x|%08x| %32s\n",
         entry, data->iv1, data->iv0, data->seq_num_mask,
         data->seq_num,
         fmt_key(buffer, data->hkey));

    dbg_dump(fd, "|  |W1| %32s | %-13x | %-16x\n",
         fmt_key(buffer, data->akey), data->ctxt_id, data->ctrl_word);

    ctxt_ctrl.regs.reg = data->ctrl_word;

    dbg_dump(fd, "|  |W2| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x| %02x\n",
         ctxt_ctrl.fields.ctxt_id,
         ctxt_ctrl.fields.seq_mask,
         ctxt_ctrl.fields.seq_type,
         ctxt_ctrl.fields.an,
         ctxt_ctrl.fields.authent_al,
         ctxt_ctrl.fields.digest_type,
         ctxt_ctrl.fields.crypto_al,
         ctxt_ctrl.fields.key,
         ctxt_ctrl.fields.encrypt_auth,
         ctxt_ctrl.fields.iv_format,
         ctxt_ctrl.fields.up_seq_num,
         ctxt_ctrl.fields.ct_len,
         ctxt_ctrl.fields.iv03,
         ctxt_ctrl.fields.iv02,
         ctxt_ctrl.fields.iv01,
         ctxt_ctrl.fields.pack_b_op,
         ctxt_ctrl.fields.top );

    return CS_OK;
}

/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display an entry in the the Egress Core Configuration 
 * table. In reality there is only one entry but it is provided to keep it similar 
 * to the other print methods. 
 *
 *  @param fd    [I] -  The file handle to write to. 
 *  @param data  [I] -  The entry to display. 
 *
 *  @return          -  CS_OK or CS_ERROR.
 *  @private
 *
 */
cs_status leeds_macsec_print_ecc_ent(
        leeds_handle_t            fd,
        uint32                    entry,
        leeds_macsec_core_ctxt_t* data)
{
    dbg_dump(fd, "| %d|%08x|%08x|%08x|%08x|%08x|%08x|%08x|%08x|%08x\n",
                 entry,
                 data->token_ctl_stat, data->prot_al_enb, data->ctxt_control,
                 data->ctxt_stat, data->intr_ctl_stat, data->sw_intr,
                 data->seq_num_thresh, data->type, data->version);
   
    return CS_OK; 
}


/*----------------------------------------------------------------------------------------------------*/
/**
 *
 * This method is called to display a single entry in the Egress Rules Token Table. 
 *
 *  @param fd     [I] -  The file handle to write to. 
 *  @param entry  [I] -  The entry number to display. 
 *  @param data   [I] -  The entry data to display. 
 *
 *  @return           -  CS_OK or CS_ERROR.
 *  @private
 *
 * 
 */
cs_status leeds_macsec_print_ert_ent(
        leeds_handle_t        fd,
        uint32                entry,
        leeds_macsec_token_t* data)
{
    dbg_dump(fd, "|%02d| %02x|%02x|%02x|%02x|%02x| %02x| %02x| %02x|%02x| %02x|%02x|%02x|%06x| %08x|%08x| %08x\n",
                 entry,
                 data->token_type, data->pass, data->direction, data->es,
                 data->sc, data->scb, data->too, data->eco, data->co,
                 data->cid_update, data->oid_valid, data->len_valid,
                 data->inp_pkt_len, data->context_ptr, data->output_id,
                 data->extended_co);
                 
    return CS_OK;
}



