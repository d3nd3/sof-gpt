
SVC_BAD = 0x00
SVC_TEMP_ENTITY = 0x01
SVC_LAYOUT = 0x02
SVC_UNUSED = 0x03
SVC_SOUND_INFO = 0x04
SVC_EFFECT = 0x05
SVC_EQUIP = 0x06
SVC_NOP = 0x07
SVC_DISCONNECT = 0x08
SVC_RECONNECT = 0x09
SVC_SOUND = 0x0a
SVC_PRINT = 0x0b
SVC_NAMEPRINT = 0x0c
SVC_STUFFTEXT = 0x0d
SVC_SERVERDATA = 0x0e
SVC_CONFIGSTRING = 0x0f
SVC_SPAWNBASELINE = 0x10
SVC_CENTERPRINT = 0x11
SVC_CAPTIONPRINT = 0x12
SVC_DOWNLOAD = 0x13
SVC_PLAYERINFO = 0x14
SVC_PACKETENTITIES = 0x15
SVC_DELTAPACKETENTITIES = 0x16
SVC_FRAME = 0x17
SVC_CULLEDEVENT = 0x18
SVC_DAMAGETEXTURE = 0x19
SVC_GHOULRELIABLE = 0x1a
SVC_GHOULUNRELIABLE = 0x1b
SVC_RIC = 0x1c
SVC_RESTART_PREDN = 0x1d
SVC_REBUILD_PRED_INV = 0x1e
SVC_COUNTDOWN = 0x1f
SVC_CINPRINT = 0x20
SVC_PLAYERNAMECOLS = 0x21
SVC_SP_PRINT = 0x22
SVC_REMOVECONFIGSTRING = 0x23
SVC_SP_PRINT_DATA_1 = 0x24
SVC_SP_PRINT_DATA_2 = 0x25
SVC_WELCOMEPRINT = 0x26
SVC_SP_PRINT_OBIT = 0x27
SVC_FORCE_CON_NOTIFY = 0x28

packet_names = [
"svc_bad",
"svc_temp_entity",
"svc_layout",
"svc_UNUSED",
"svc_sound_info",
"svc_effect",
"svc_equip",
"svc_nop",
"svc_disconnect",
"svc_reconnect",
"svc_sound",
"svc_print",
"svc_nameprint",
"svc_stufftext",
"svc_serverdata",
"svc_configstring",
"svc_spawnbaseline",
"svc_centerprint",
"svc_captionprint",
"svc_download",
"svc_playerinfo",
"svc_packetentities",
"svc_deltapacketentities",
"svc_frame",
"svc_culledEvent",
"svc_damagetexture",
"svc_ghoulreliable",
"svc_ghoulunreliable",
"svc_ric",
"svc_restart_predn",
"svc_rebuild_pred_inv",
"svc_countdown",
"svc_cinprint",
"svc_playernamecols",
"svc_sp_print",
"svc_removeconfigstring",
"svc_sp_print_data_1",
"svc_sp_print_data_2",
"svc_welcomeprint",
"svc_sp_print_obit",
"svc_force_con_notify"
]


def packetIDtoName(packet):
	if packet < len(packet_names):
		return packet_names[packet]
	return None
