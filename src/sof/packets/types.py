
# ucmd_t myucmds[] =
# {
# 	// auto issued
# 	{"new", 0x20062780},
# 	{"configstrings", (unsigned int)o_sofplus + 0x174E0},
# 	{"baselines", (unsigned int)o_sofplus + 0x17530},
# 	{"begin", (unsigned int)o_sofplus + 0x17570},
# 	{"nextserver", 0x20063530},
# 	{"disconnect", 0x20063450},
# 	{"download", (unsigned int)o_sofplus + 0x175E0},
# 	{"nextdl", 0x20063040}, //
# 	{"ghoulstrings", (unsigned int)o_sofplus + 0x17660},
# 	{"sv_precache",0x20062F20},
# 	// deleted by ctrl
# 	//{"info", SV_ShowServerinfo_f},//0x20063470
# 	/*
# 	ctrl has shifted sv_precache up and wants info to not exist
# 	*/
# 	{",check",myCheck_f},
# 	{NULL, NULL}
# };

CLC_BAD = '\x00'
CLC_NOP = '\x01'
CLC_MOVE = '\x02'
CLC_USERINFO = '\x03'
CLC_STRINGCMD = '\x04'

SVC_BAD = '\x00'
SVC_TEMP_ENTITY = '\x01'
SVC_LAYOUT = '\x02'
SVC_UNUSED = '\x03'
SVC_SOUND_INFO = '\x04'
SVC_EFFECT = '\x05'
SVC_EQUIP = '\x06'
SVC_NOP = '\x07'
SVC_DISCONNECT = '\x08'
SVC_RECONNECT = '\x09'
SVC_SOUND = '\x0a'
SVC_PRINT = '\x0b'
SVC_NAMEPRINT = '\x0c'
SVC_STUFFTEXT = '\x0d'
SVC_SERVERDATA = '\x0e'
SVC_CONFIGSTRING = '\x0f'
SVC_SPAWNBASELINE = '\x10'
SVC_CENTERPRINT = '\x11'
SVC_CAPTIONPRINT = '\x12'
SVC_DOWNLOAD = '\x13'
SVC_PLAYERINFO = '\x14'
SVC_PACKETENTITIES = '\x15'
SVC_DELTAPACKETENTITIES = '\x16'
SVC_FRAME = '\x17'
SVC_CULLEDEVENT = '\x18'
SVC_DAMAGETEXTURE = '\x19'
SVC_GHOULRELIABLE = '\x1a'
SVC_GHOULUNRELIABLE = '\x1b'
SVC_RIC = '\x1c'
SVC_RESTART_PREDN = '\x1d'
SVC_REBUILD_PRED_INV = '\x1e'
SVC_COUNTDOWN = '\x1f'
SVC_CINPRINT = '\x20'
SVC_PLAYERNAMECOLS = '\x21'
SVC_SP_PRINT = '\x22'
SVC_REMOVECONFIGSTRING = '\x23'
SVC_SP_PRINT_DATA_1 = '\x24'
SVC_SP_PRINT_DATA_2 = '\x25'
SVC_WELCOMEPRINT = '\x26'
SVC_SP_PRINT_OBIT = '\x27'
SVC_FORCE_CON_NOTIFY = '\x28'


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
