import socket
import random
import sys
import struct
import time
import hashlib
import errno
import os


from ask_question import libVersion as gtp_ask

class PACKET_SVC:
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
"svc_force_con_notify",
]

def packetIDtoName(packet):
	if packet < len(packet_names):
		return packet_names[packet]
	return "bad data"


chktbl2 = b'\x60\xe5\x60\x3e\x00\x00\x00\x00\xdf\xbf\x79\x3f\x61\xfe\x8a\x3d\x54\xe3\x55\x3e\xdf\xbf\x79\x3f\xa1\x67\xdb\x3e\x00\x00\x00\x00\xbe\x4d\x67\x3f\xe5\x62\x94\x3e\x5a\x9e\x57\x3e\x82\x02\x6f\x3f\x5f\x99\x07\x3e\x86\xaa\xd0\x3e\xbe\x4d\x67\x3f\xf2\xd2\x1d\x3f\x00\x00\x00\x00\x19\x90\x49\x3f\x2b\x89\x00\x3f\x20\x7f\x59\x3e\x88\x9c\x56\x3f\x6a\xdd\xb6\x3e\x76\xe2\xd2\x3e\x88\x9c\x56\x3f\xcb\x14\x43\x3e\x76\x19\x16\x3f\x19\x90\x49\x3f\x1d\x3d\x46\x3f\x00\x00\x00\x00\xca\xfa\x21\x3f\xb8\xe4\x30\x3f\xe2\xca\x59\x3e\xa9\xdc\x30\x3f\xf1\xb7\x11\x3f\xbe\xbd\xd3\x3e\x89\xea\x35\x3f\x86\xe4\xd4\x3e\x01\x69\x17\x3f\xa9\xdc\x30\x3f\x7d\x09\x75\x3e\x4c\x89\x3c\x3f\xca\xfa\x21\x3f\x2b\xf9\x64\x3f\x00\x00\x00\x00\x3c\xf9\xe4\x3e\xe9\x9c\x57\x3f\x54\xe3\x55\x3e\x64\x76\xfe\x3e\x49\xb9\x3f\x3f\x86\xaa\xd0\x3e\x59\xc3\x05\x3f\x03\x79\x1e\x3f\x76\x19\x16\x3f\x59\xc3\x05\x3f\x4d\xf7\xea\x3e\x4c\x89\x3c\x3f\x64\x76\xfe\x3e\x62\x83\x8d\x3e\x44\xc4\x59\x3f\x3c\xf9\xe4\x3e\xbf\xf1\x35\xbe\xb1\x30\x04\x3e\xdf\xbf\x79\x3f\xae\xb6\xe2\xbd\x5d\x70\xae\x3e\x82\x02\x6f\x3f\x91\x80\xb1\xbe\x8c\xf6\x80\x3e\xbe\x4d\x67\x3f\xb0\xe3\x3f\xbd\x13\x0c\x0b\x3f\x78\x9c\x56\x3f\x06\x0e\x90\xbe\xfd\x14\xef\x3e\x78\x9c\x56\x3f\x57\x5d\xff\xbe\x6e\x88\xb9\x3e\x19\x90\x49\x3f\xba\x4d\x38\x3c\xa6\x0f\x39\x3f\xa9\xdc\x30\x3f\x59\xa3\x5e\xbe\x6a\x4d\x2b\x3f\x89\xea\x35\x3f\x4c\x36\xde\xbe\x5b\x06\x14\x3f\xa9\xdc\x30\x3f\xee\x60\x20\xbf\x20\x0b\xe9\x3e\xca\xfa\x21\x3f\xea\x5d\x7c\x3d\x79\x95\x5d\x3f\x64\x76\xfe\x3e\x57\xec\x1f\xbe\xbc\x94\x56\x3f\x59\xc3\x05\x3f\x86\x90\xbb\xbe\x8b\x19\x45\x3f\x59\xc3\x05\x3f\x21\x01\x0f\xbf\x76\xfe\x29\x3f\x64\x76\xfe\x3e\x4f\x3e\x39\xbf\x4f\x96\x06\x3f\x3c\xf9\xe4\x3e\xbf\xf1\x35\xbe\xb1\x30\x04\xbe\xdf\xbf\x79\x3f\x72\x6a\xb7\xbe\x00\x00\x00\x00\x82\x02\x6f\x3f\x91\x80\xb1\xbe\x8c\xf6\x80\xbe\xbe\x4d\x67\x3f\xa1\xf2\x07\xbf\x6b\x7e\xfc\x3d\x78\x9c\x56\x3f\xa1\xf2\x07\xbf\xf1\x7e\xfc\xbd\x78\x9c\x56\x3f\x57\x5d\xff\xbe\x6e\x88\xb9\xbe\x19\x90\x49\x3f\x1d\x1d\x2f\xbf\xfa\xb3\x6f\x3e\xa9\xdc\x30\x3f\x36\x1e\x34\xbf\x00\x00\x00\x00\x89\xea\x35\x3f\x1d\x1d\x2f\xbf\x3e\xb4\x6f\xbe\xa9\xdc\x30\x3f\xdd\x60\x20\xbf\x20\x0b\xe9\xbe\xca\xfa\x21\x3f\x5d\xdd\x4d\xbf\xc7\xf2\xa6\x3e\x64\x76\xfe\x3e\xf4\x6e\x58\xbf\x0f\x48\xe2\x3d\x59\xc3\x05\x3f\xf4\x6e\x58\xbf\x0f\x48\xe2\xbd\x59\xc3\x05\x3f\x5d\xdd\x4d\xbf\xc7\xf2\xa6\xbe\x64\x76\xfe\x3e\x4f\x3e\x39\xbf\x4f\x96\x06\xbf\x3c\xf9\xe4\x3e\x61\xfe\x8a\x3d\x54\xe3\x55\xbe\xdf\xbf\x79\x3f\xae\xb6\xe2\xbd\x5d\x70\xae\xbe\x82\x02\x6f\x3f\xa2\x99\x07\x3e\x86\xaa\xd0\xbe\xbe\x4d\x67\x3f\x06\x0e\x90\xbe\xfd\x14\xef\xbe\x88\x9c\x56\x3f\xb0\xe3\x3f\xbd\x13\x0c\x0b\xbf\x88\x9c\x56\x3f\xcb\x14\x43\x3e\x76\x19\x16\xbf\x19\x90\x49\x3f\x4c\x36\xde\xbe\x5b\x06\x14\xbf\x98\xdc\x30\x3f\x59\xa3\x5e\xbe\x6a\x4d\x2b\xbf\x89\xea\x35\x3f\xba\x4d\x38\x3c\xa6\x0f\x39\xbf\x98\xdc\x30\x3f\x7d\x09\x75\x3e\x4c\x89\x3c\xbf\xca\xfa\x21\x3f\x21\x01\x0f\xbf\x76\xfe\x29\xbf\x64\x76\xfe\x3e\x86\x90\xbb\xbe\x8b\x19\x45\xbf\x59\xc3\x05\x3f\x57\xec\x1f\xbe\xbc\x94\x56\xbf\x59\xc3\x05\x3f\xf6\x5e\x7c\x3d\x79\x95\x5d\xbf\x64\x76\xfe\x3e\x62\x83\x8d\x3e\x44\xc4\x59\xbf\x3c\xf9\xe4\x3e\xe5\x62\x94\x3e\x5a\x9e\x57\xbe\x82\x02\x6f\x3f\x6a\xdd\xb6\x3e\x76\xe2\xd2\xbe\x78\x9c\x56\x3f\x2b\x89\x00\x3f\x20\x7f\x59\xbe\x78\x9c\x56\x3f\x86\xe4\xd4\x3e\x01\x69\x17\xbf\x98\xdc\x30\x3f\xf1\xb7\x11\x3f\xbe\xbd\xd3\xbe\x89\xea\x35\x3f\xb8\xe4\x30\x3f\xe2\xca\x59\xbe\x98\xdc\x30\x3f\x4d\xf7\xea\x3e\x4c\x89\x3c\xbf\x64\x76\xfe\x3e\x03\x79\x1e\x3f\x76\x19\x16\xbf\x59\xc3\x05\x3f\x49\xb9\x3f\x3f\x86\xaa\xd0\xbe\x59\xc3\x05\x3f\xe9\x9c\x57\x3f\x54\xe3\x55\xbe\x64\x76\xfe\x3e\x8c\xb9\x73\x3f\xb1\x30\x04\xbe\xd5\x03\x8e\x3e\x8c\xb9\x73\x3f\xb1\x30\x04\x3e\xd5\x03\x8e\x3e\x3a\x93\x76\x3f\x6a\xf6\x80\xbe\x42\x7c\xc0\x3d\x36\xca\x7e\x3f\x00\x00\x00\x00\x54\xe6\xc6\x3d\x29\x93\x76\x3f\x8c\xf6\x80\x3e\x42\x7c\xc0\x3d\x7c\x62\x6d\x3f\x6e\x88\xb9\xbe\x42\x7c\xc0\xbd\x7b\xc0\x7c\x3f\x6b\x7e\xfc\xbd\x8c\xf2\xcc\xbd\x7b\xc0\x7c\x3f\xf1\x7e\xfc\x3d\x8c\xf2\xcc\xbd\x7c\x62\x6d\x3f\x6e\x88\xb9\x3e\x42\x7c\xc0\xbd\x35\x9a\x58\x3f\x20\x0b\xe9\xbe\xd5\x03\x8e\xbe\xd8\x80\x6c\x3f\xfa\xb3\x6f\xbe\x13\x10\x9b\xbe\x0f\x43\x73\x3f\x00\x00\x00\x00\x80\x7e\x9f\xbe\xd8\x80\x6c\x3f\x3e\xb4\x6f\x3e\x13\x10\x9b\xbe\x35\x9a\x58\x3f\x20\x0b\xe9\x3e\xd5\x03\x8e\xbe\x4f\x3e\x39\x3f\x4f\x96\x06\xbf\x3c\xf9\xe4\xbe\x5d\xdd\x4d\x3f\xc7\xf2\xa6\xbe\x64\x76\xfe\xbe\xf4\x6e\x58\x3f\x0f\x48\xe2\xbd\x59\xc3\x05\xbf\xf4\x6e\x58\x3f\x0f\x48\xe2\x3d\x59\xc3\x05\xbf\x5d\xdd\x4d\x3f\xc7\xf2\xa6\x3e\x64\x76\xfe\xbe\x4f\x3e\x39\x3f\x4f\x96\x06\x3f\x3c\xf9\xe4\xbe\x9e\x7d\xd5\x3e\x79\x95\x5d\x3f\xd5\x03\x8e\x3e\x4c\x8a\x2f\x3e\x21\x02\x72\x3f\xd5\x03\x8e\x3e\x7b\x85\x09\x3f\xbc\x94\x56\x3f\x42\x7c\xc0\x3d\xfb\x77\x9d\x3e\xd2\x51\x72\x3f\x54\xe6\xc6\x3d\xa2\xec\x6d\x3d\xb9\x6e\x7e\x3f\x42\x7c\xc0\x3d\x03\x95\x21\x3f\x8b\x19\x45\x3f\x42\x7c\xc0\xbd\x64\x3e\xd8\x3e\xdc\xa0\x66\x3f\x8c\xf2\xcc\xbd\xa7\x59\x40\x3e\x70\x22\x7a\x3f\x8c\xf2\xcc\xbd\xa2\xec\x6d\xbd\xb9\x6e\x7e\x3f\x42\x7c\xc0\xbd\xa9\xc0\x31\x3f\x76\xfe\x29\x3f\xd5\x03\x8e\xbe\x90\x13\x02\x3f\xe4\x68\x4e\x3f\x13\x10\x9b\xbe\x1d\x58\x96\x3e\x1d\x5b\x67\x3f\x80\x7e\x9f\xbe\x99\xb9\x80\x3d\x2e\x72\x73\x3f\x13\x10\x9b\xbe\x4c\x8a\x2f\xbe\x21\x02\x72\x3f\xd5\x03\x8e\xbe\x21\x01\x0f\x3f\x76\xfe\x29\x3f\x64\x76\xfe\xbe\x86\x90\xbb\x3e\x8b\x19\x45\x3f\x59\xc3\x05\xbf\x57\xec\x1f\x3e\xbc\x94\x56\x3f\x59\xc3\x05\xbf\xea\x5d\x7c\xbd\x79\x95\x5d\x3f\x64\x76\xfe\xbe\x62\x83\x8d\xbe\x44\xc4\x59\x3f\x3c\xf9\xe4\xbe\xa9\xc0\x31\xbf\x76\xfe\x29\x3f\xd5\x03\x8e\x3e\x35\x9a\x58\xbf\x20\x0b\xe9\x3e\xd5\x03\x8e\x3e\x03\x95\x21\xbf\x8b\x19\x45\x3f\x42\x7c\xc0\x3d\x21\x21\x4e\xbf\x05\xc3\x15\x3f\x54\xe6\xc6\x3d\x7c\x62\x6d\xbf\x6e\x88\xb9\x3e\x42\x7c\xc0\x3d\x7b\x85\x09\xbf\xbc\x94\x56\x3f\x42\x7c\xc0\xbd\xd0\xed\x39\xbf\x11\x19\x2e\x3f\x8c\xf2\xcc\xbd\x46\x08\x5f\xbf\x3d\x0f\xf6\x3e\x8c\xf2\xcc\xbd\x3a\x93\x76\xbf\x6a\xf6\x80\x3e\x42\x7c\xc0\xbd\x9e\x7d\xd5\xbe\x79\x95\x5d\x3f\xd5\x03\x8e\xbe\x93\x1c\x1c\xbf\x80\x7e\x3b\x3f\x13\x10\x9b\xbe\x96\xcd\x44\xbf\x59\xfc\x0e\x3f\x80\x7e\x9f\xbe\x08\x8f\x62\xbf\x6f\x10\xb5\x3e\x13\x10\x9b\xbe\x8c\xb9\x73\xbf\xb1\x30\x04\x3e\xd5\x03\x8e\xbe\x4d\xf7\xea\xbe\x4c\x89\x3c\x3f\x64\x76\xfe\xbe\x03\x79\x1e\xbf\x76\x19\x16\x3f\x59\xc3\x05\xbf\x49\xb9\x3f\xbf\x86\xaa\xd0\x3e\x59\xc3\x05\xbf\xe9\x9c\x57\xbf\x54\xe3\x55\x3e\x64\x76\xfe\xbe\x2b\xf9\x64\xbf\x00\x00\x00\x00\x3c\xf9\xe4\xbe\x35\x9a\x58\xbf\x20\x0b\xe9\xbe\xd5\x03\x8e\x3e\xa9\xc0\x31\xbf\x76\xfe\x29\xbf\xd5\x03\x8e\x3e\x6b\x62\x6d\xbf\x6e\x88\xb9\xbe\x42\x7c\xc0\x3d\x21\x21\x4e\xbf\x05\xc3\x15\xbf\x54\xe6\xc6\x3d\x03\x95\x21\xbf\x8b\x19\x45\xbf\x42\x7c\xc0\x3d\x3a\x93\x76\xbf\x8c\xf6\x80\xbe\x42\x7c\xc0\xbd\x46\x08\x5f\xbf\x3d\x0f\xf6\xbe\x8c\xf2\xcc\xbd\xd0\xed\x39\xbf\x11\x19\x2e\xbf\x8c\xf2\xcc\xbd\x7b\x85\x09\xbf\xbc\x94\x56\xbf\x42\x7c\xc0\xbd\x8c\xb9\x73\xbf\xb1\x30\x04\xbe\xd5\x03\x8e\xbe\x08\x8f\x62\xbf\x6f\x10\xb5\xbe\x13\x10\x9b\xbe\x96\xcd\x44\xbf\x59\xfc\x0e\xbf\x80\x7e\x9f\xbe\x93\x1c\x1c\xbf\x80\x7e\x3b\xbf\x13\x10\x9b\xbe\x9e\x7d\xd5\xbe\x79\x95\x5d\xbf\xd5\x03\x8e\xbe\xe9\x9c\x57\xbf\x97\xe3\x55\xbe\x64\x76\xfe\xbe\x49\xb9\x3f\xbf\x86\xaa\xd0\xbe\x59\xc3\x05\xbf\x03\x79\x1e\xbf\x76\x19\x16\xbf\x59\xc3\x05\xbf\x4d\xf7\xea\xbe\x4c\x89\x3c\xbf\x64\x76\xfe\xbe\x62\x83\x8d\xbe\x44\xc4\x59\xbf\x3c\xf9\xe4\xbe\x4c\x8a\x2f\x3e\x21\x02\x72\xbf\xd5\x03\x8e\x3e\x9e\x7d\xd5\x3e\x79\x95\x5d\xbf\xd5\x03\x8e\x3e\xa2\xec\x6d\x3d\xb9\x6e\x7e\xbf\x42\x7c\xc0\x3d\xfb\x77\x9d\x3e\xd2\x51\x72\xbf\x54\xe6\xc6\x3d\x7b\x85\x09\x3f\xab\x94\x56\xbf\x42\x7c\xc0\x3d\xa2\xec\x6d\xbd\xb9\x6e\x7e\xbf\x42\x7c\xc0\xbd\xa7\x59\x40\x3e\x70\x22\x7a\xbf\x8c\xf2\xcc\xbd\x64\x3e\xd8\x3e\xcb\xa0\x66\xbf\x8c\xf2\xcc\xbd\x03\x95\x21\x3f\x7a\x19\x45\xbf\x42\x7c\xc0\xbd\x4c\x8a\x2f\xbe\x21\x02\x72\xbf\xd5\x03\x8e\xbe\x99\xb9\x80\x3d\x2e\x72\x73\xbf\x13\x10\x9b\xbe\x1d\x58\x96\x3e\x1d\x5b\x67\xbf\x80\x7e\x9f\xbe\x90\x13\x02\x3f\xe4\x68\x4e\xbf\x13\x10\x9b\xbe\xa9\xc0\x31\x3f\x76\xfe\x29\xbf\xd5\x03\x8e\xbe\xea\x5d\x7c\xbd\x79\x95\x5d\xbf\x64\x76\xfe\xbe\x57\xec\x1f\x3e\xbc\x94\x56\xbf\x59\xc3\x05\xbf\x86\x90\xbb\x3e\x8b\x19\x45\xbf\x59\xc3\x05\xbf\x21\x01\x0f\x3f\x76\xfe\x29\xbf\x64\x76\xfe\xbe\x21\x21\x4e\x3f\x05\xc3\x15\x3f\x54\xe6\xc6\xbd\xd0\xed\x39\x3f\x11\x19\x2e\x3f\x8c\xf2\xcc\x3d\x46\x08\x5f\x3f\x3d\x0f\xf6\x3e\x8c\xf2\xcc\x3d\x93\x1c\x1c\x3f\x80\x7e\x3b\x3f\x13\x10\x9b\x3e\x96\xcd\x44\x3f\x59\xfc\x0e\x3f\x80\x7e\x9f\x3e\x08\x8f\x62\x3f\x6f\x10\xb5\x3e\x13\x10\x9b\x3e\xfb\x77\x9d\xbe\xd2\x51\x72\x3f\x54\xe6\xc6\xbd\x64\x3e\xd8\xbe\xcb\xa0\x66\x3f\x8c\xf2\xcc\x3d\xa7\x59\x40\xbe\x70\x22\x7a\x3f\x8c\xf2\xcc\x3d\x90\x13\x02\xbf\xe4\x68\x4e\x3f\x13\x10\x9b\x3e\x1d\x58\x96\xbe\x1d\x5b\x67\x3f\x80\x7e\x9f\x3e\x99\xb9\x80\xbd\x2e\x72\x73\x3f\x13\x10\x9b\x3e\x36\xca\x7e\xbf\x00\x00\x00\x00\x54\xe6\xc6\xbd\x7b\xc0\x7c\xbf\xf1\x7e\xfc\xbd\x8c\xf2\xcc\x3d\x7b\xc0\x7c\xbf\x6b\x7e\xfc\x3d\x8c\xf2\xcc\x3d\xd8\x80\x6c\xbf\x3e\xb4\x6f\xbe\x13\x10\x9b\x3e\x0f\x43\x73\xbf\x00\x00\x00\x00\x80\x7e\x9f\x3e\xd8\x80\x6c\xbf\xfa\xb3\x6f\x3e\x13\x10\x9b\x3e\xfb\x77\x9d\xbe\xd2\x51\x72\xbf\x54\xe6\xc6\xbd\xa7\x59\x40\xbe\x70\x22\x7a\xbf\x8c\xf2\xcc\x3d\x64\x3e\xd8\xbe\xdc\xa0\x66\xbf\x8c\xf2\xcc\x3d\x99\xb9\x80\xbd\x2e\x72\x73\xbf\x13\x10\x9b\x3e\x1d\x58\x96\xbe\x1d\x5b\x67\xbf\x80\x7e\x9f\x3e\x90\x13\x02\xbf\xe4\x68\x4e\xbf\x13\x10\x9b\x3e\x21\x21\x4e\x3f\xf4\xc2\x15\xbf\x54\xe6\xc6\xbd\x46\x08\x5f\x3f\x3d\x0f\xf6\xbe\x8c\xf2\xcc\x3d\xd0\xed\x39\x3f\x11\x19\x2e\xbf\x8c\xf2\xcc\x3d\x08\x8f\x62\x3f\x6f\x10\xb5\xbe\x13\x10\x9b\x3e\x96\xcd\x44\x3f\x59\xfc\x0e\xbf\x80\x7e\x9f\x3e\x93\x1c\x1c\x3f\x80\x7e\x3b\xbf\x13\x10\x9b\x3e\x61\xfe\x8a\xbd\x54\xe3\x55\x3e\xdf\xbf\x79\xbf\xbf\xf1\x35\x3e\xb1\x30\x04\x3e\xdf\xbf\x79\xbf\x5f\x99\x07\xbe\x86\xaa\xd0\x3e\xbe\x4d\x67\xbf\xae\xb6\xe2\x3d\x5d\x70\xae\x3e\x82\x02\x6f\xbf\x91\x80\xb1\x3e\x8c\xf6\x80\x3e\xbe\x4d\x67\xbf\xcb\x14\x43\xbe\x76\x19\x16\x3f\x19\x90\x49\xbf\xb0\xe3\x3f\x3d\x13\x0c\x0b\x3f\x88\x9c\x56\xbf\x06\x0e\x90\x3e\xfd\x14\xef\x3e\x88\x9c\x56\xbf\x57\x5d\xff\x3e\x6e\x88\xb9\x3e\x19\x90\x49\xbf\x7d\x09\x75\xbe\x4c\x89\x3c\x3f\xca\xfa\x21\xbf\xba\x4d\x38\xbc\xa6\x0f\x39\x3f\xa9\xdc\x30\xbf\x59\xa3\x5e\x3e\x6a\x4d\x2b\x3f\x89\xea\x35\xbf\x4c\x36\xde\x3e\x5b\x06\x14\x3f\xa9\xdc\x30\xbf\xee\x60\x20\x3f\x20\x0b\xe9\x3e\xca\xfa\x21\xbf\x60\xe5\x60\xbe\x00\x00\x00\x00\xdf\xbf\x79\xbf\xa1\x67\xdb\xbe\x00\x00\x00\x00\xbe\x4d\x67\xbf\xe5\x62\x94\xbe\x5a\x9e\x57\x3e\x82\x02\x6f\xbf\xf2\xd2\x1d\xbf\x00\x00\x00\x00\x19\x90\x49\xbf\x2b\x89\x00\xbf\x20\x7f\x59\x3e\x88\x9c\x56\xbf\x6a\xdd\xb6\xbe\x76\xe2\xd2\x3e\x88\x9c\x56\xbf\x1d\x3d\x46\xbf\x00\x00\x00\x00\xca\xfa\x21\xbf\xb8\xe4\x30\xbf\xe2\xca\x59\x3e\xa9\xdc\x30\xbf\xf1\xb7\x11\xbf\xbe\xbd\xd3\x3e\x89\xea\x35\xbf\x86\xe4\xd4\xbe\x01\x69\x17\x3f\xa9\xdc\x30\xbf\x61\xfe\x8a\xbd\x54\xe3\x55\xbe\xdf\xbf\x79\xbf\x5f\x99\x07\xbe\x86\xaa\xd0\xbe\xbe\x4d\x67\xbf\xe5\x62\x94\xbe\x5a\x9e\x57\xbe\x82\x02\x6f\xbf\xcb\x14\x43\xbe\x76\x19\x16\xbf\x19\x90\x49\xbf\x6a\xdd\xb6\xbe\x76\xe2\xd2\xbe\x78\x9c\x56\xbf\x2b\x89\x00\xbf\x20\x7f\x59\xbe\x78\x9c\x56\xbf\x7d\x09\x75\xbe\x4c\x89\x3c\xbf\xca\xfa\x21\xbf\x86\xe4\xd4\xbe\x01\x69\x17\xbf\xa9\xdc\x30\xbf\xf1\xb7\x11\xbf\xe0\xbd\xd3\xbe\x89\xea\x35\xbf\xb8\xe4\x30\xbf\xe2\xca\x59\xbe\xa9\xdc\x30\xbf\xbf\xf1\x35\x3e\xb1\x30\x04\xbe\xdf\xbf\x79\xbf\x91\x80\xb1\x3e\x6a\xf6\x80\xbe\xbe\x4d\x67\xbf\xae\xb6\xe2\x3d\x5d\x70\xae\xbe\x82\x02\x6f\xbf\x57\x5d\xff\x3e\x6e\x88\xb9\xbe\x19\x90\x49\xbf\x06\x0e\x90\x3e\xfd\x14\xef\xbe\x78\x9c\x56\xbf\xb0\xe3\x3f\x3d\x13\x0c\x0b\xbf\x78\x9c\x56\xbf\xee\x60\x20\x3f\x20\x0b\xe9\xbe\xca\xfa\x21\xbf\x4c\x36\xde\x3e\x5b\x06\x14\xbf\x98\xdc\x30\xbf\x59\xa3\x5e\x3e\x6a\x4d\x2b\xbf\x89\xea\x35\xbf\xba\x4d\x38\xbc\xa6\x0f\x39\xbf\x98\xdc\x30\xbf\x72\x6a\xb7\x3e\x00\x00\x00\x00\x82\x02\x6f\xbf\xa1\xf2\x07\x3f\xf1\x7e\xfc\x3d\x78\x9c\x56\xbf\xb2\xf2\x07\x3f\x6b\x7e\xfc\xbd\x78\x9c\x56\xbf\x1d\x1d\x2f\x3f\x3e\xb4\x6f\x3e\x98\xdc\x30\xbf\x36\x1e\x34\x3f\x00\x00\x00\x00\x89\xea\x35\xbf\x1d\x1d\x2f\x3f\xfa\xb3\x6f\xbe\x98\xdc\x30\xbf'

bitpos = 0
def dataToBits(stream, indata, bits, nosign=True):
	global bitpos
	if not nosign:
		if bits > 1:
			if bits <=8:
				if indata[0] < 0:
					# make positive and write a 1 in front
					indata[0] = -indata[0]
					# bits = bits - 1;
					dataToBits(stream,one,1)
				else:
					# bits = bits - 1;
					dataToBits(stream,zero,1)
			elif bits <= 16:
				s = struct.unpack_from('<h',indata,0)
				if s < 0:
					struct.unpack_into('<h',indata,0,-s)
					# bits = bits - 1;
					dataToBits(stream,one,1)
				else:
					# bits = bits - 1;
					dataToBits(stream,zero,1)
			elif bits <= 32:
				i = struct.unpack_from('<i',indata,0)
				if i < 0:
					# bits = bits - 1;
					struct.unpack_into('<i',indata,0,-i)
					dataToBits(stream,one,1)
				else:
					dataToBits(stream,zero,1)
			bits = bits - 1
	
	# if ( bits <=8 ) {
	# 	printf("extract %i bits from byte %02X\n",bits,*(unsigned char*)indata);
	# } else
	# if ( bits <= 16 ) {
	# 	printf("extract %i bits from short %04X :: %hu\n",bits,*(short*)indata,*(short*)indata);
	# } else
	# if ( bits <= 32 ) {
	# 	printf("extract %i bits from dword/float %08X :: %d :: %f\n",bits,*(int*)indata,*(int*)indata,*(float*)indata);
	# }
	# iterate bits
	
	for i in range(bits):
		# convert bitpos into byte?
		currentByte = int(bitpos/8)
		inByte = int(i/8)
		# get the bit from inshort , grab it from right to left (normal)
		targetbit = indata[inByte] & (1<<(i % 8))

		# printf("byte %i bit %i before : %02X\n",currentByte,bitpos,stream[currentByte]);


		# pick teh bit from the right to left (normal)
		# unsigned char out_bitmask = one << (7-(bitpos % 8));
		out_bitmask = 1 << (bitpos % 8)
		# is it a 1 or a 0 ?
		if targetbit:
			# case BIT is 1
			# printf("its 1\n");
			# write the bit to the stream
			# print(f"current byte = {currentByte}\n")
			# print(f"out_bitmask = {out_bitmask}\n")

			stream[currentByte] = stream[currentByte] | out_bitmask
		else:
			# case BIT is 0
			# printf("its 0\n");
			# write the bit to the stream
			stream[currentByte] = stream[currentByte] & ~out_bitmask
		bitpos += 1

	# for ( int i = 0;  i < 64; i ++ ) {
	# printf( "%02X ",lol[i] );
	# }
	# printf("\n");



# bytes and bytearray are integers
def	COM_BlockSequenceCRCByte (base, sequence):
	p = memoryview(chktbl2)
	p = p[(sequence % 2996):]

	# max total len = 64
	if len(base) > 60:
		# truncate to 60 length
		base = base[:60]


	base.append((sequence & 0xff) ^ p[0])
	base.append(p[1])
	base.append(((sequence>>8) & 0xff) ^ p[2])
	base.append(p[3])
	
	# md5 here
	# print(hashlib.new('md4',base).hexdigest())

	# print(f"base is " + "".join("\\x{0:02x}".format(x) for x in base))

	h = hashlib.new('md4',base).digest()
	d1 = struct.unpack_from('<I',h,0)[0]
	d2 = struct.unpack_from('<I',h,4)[0]
	d3 = struct.unpack_from('<I',h,8)[0]
	d4 = struct.unpack_from('<I',h,12)[0]
	# print(hex(d1))
	# print(hex(d2))
	# print(hex(d3))
	# print(hex(d4))
	checksum = (d1 ^ d2 ^ d3 ^ d4) 
	# print(f'checksum is {checksum}')
	# print(f'checksum is {checksum& 0xff}')
	return checksum & 0xff;

class Bot:
	def __init__(self,name):
		self.map = ""
		self.mapname = ""
		self.playernum = -1
		self.precache = ""
		self.start_time = 0
		self.lastServerFrame = -1
		self.name = name

		self.setup_userinfo()

	def init_timer(self):
		self.start_time = time.time()

	def make_userinfo(self):
		d = self.userinfo
		s = '\"'
		for key, value in d.items():
			s += '\\' + key + '\\' + value
		s += '\"'
		return s
	def setup_userinfo(self):
		self.userinfo = {}
		d = self.userinfo
		
		d["predicting"]='0'
		d["spectator_password"]='specme'
		d["password"]='nopass'
		d["cl_violence"]='0'
		d["spectator"]='0'
		d["skin"]='dekker'
		d["teamname"]='The Order'
		d["fov"]='95'
		d["msg"]='0'
		d["rate"]='15000'
		d["allow_download_models"]='1'
		d["team_red_blue"]='0'
		d["name"]=self.name


class Parser:
	"""
		parse a null terminated string
		returns a tuple containing the string parsed
		and the remaining of buffer without the string
	"""
	def string(self,buf):
		startstr = buf
		count = 0
		while buf:
			if buf[0] == 0x00: #or view is none
				buf = buf[1:]
				break;
			buf = buf[1:]
			count += 1
		return (startstr[:count],buf)

	"""
		parse a stufftext type packet
		returns list of mirror packets
		seperates newline and removes 'cmd ' from them
	"""

	def stufftext(self,buf,conn):
		b = buf.tobytes().decode('ISO 8859-1')
		b = b.split("\n")
		# return only 'cmd' stufftexts but remove cmd from front
		retlist = [each[4:] for each in b if each and each.find("cmd ",0) >=0]
		
		# process non 'cmd' stufftexts...
		for a in b:
			if a and a.find("cmd ",0) < 0:
				if a.find("precache ",0) == 0:
					conn.bot.precache = a[9:]
					conn.send(True,"\x04download maps/dm/{}.eal\x00".format(conn.bot.mapname).encode('ISO 8859-1'));
					conn.i_downloading = 1
					print("SERVED BY PRECACHE STUFFTEXT\n")
				elif a.find("reconnect",0) == 0:
					print("They want you to reconnect by stufftext\n");
					# conn.connected = False
					# conn.bot.lastServerFrame = -1
					# conn.get_challenge()
					# conn.connect()
					# conn.out_seq = 0
					# conn.in_seq = 0
					# conn.reliable_s = 1
					conn.new()
					
		return retlist

class Connection:
	def __init__(self,server,port,bot):
		self.bot = bot
		self.server = (server,port)
		self.last_rel_sent,self.reliable_r_ack,self.reliable_s,self.reliable_r,self.out_seq,self.in_seq,self.in_ack=0,0,0,0,0,0,0
		self.busy = False
		self.qport=self.rand(5)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.settimeout(0)
		self.pars = Parser()
		self.connected = False
		self.expectmapname = False
		self.i_downloading = 0
		
	def rand(self,len):
		rand = []
		for x in range(0,len):
			i = random.randint(0,9);
			rand += str(i)
		return int(''.join(map(str, rand)))
	def get_challenge(self):
		print("[unconnected] Sending getchallenge to server")
		self.mychal = self.rand(10)
		buf = "getchallenge {}\x0A\x00".format(self.mychal)
		self.send(False,buf.encode('ISO 8859-1'))
		while True:
			o = self.recv()
			# break only once we got the data
			if type(o) is memoryview:
				self.chal = bytes.decode(bytes(o[10:]),'ISO 8859-1')
				break

		print(f"[unconnected] received challenge {self.chal}")
		

	def connect(self):
		print("[unconnected] Sending connect to server")
		#sprintf(tmp_buf,"connect 33 %hu %lu %lu 3.14 "userinfo"\x0A\x00",qport,i_chal,mychal);
		self.qport = self.rand(4)
		buf = "connect 33 {} {} {} 3.14 {}\x0A".format(self.qport,self.chal,self.mychal,self.bot.make_userinfo())
		self.send(False,buf.encode('ISO 8859-1'))
		while True:
			o = self.recv()
			if type(o) is memoryview:
				break

	def new(self):
		print("[connected] Sending new to server")
		buf = "\x04new\x00"
		print(buf.encode('ISO 8859-1'))
		self.send(True,buf.encode('ISO 8859-1'))


	def send(self,rel,data):
		
		# if rel:
		# 	send_reliable = False
		# 	if self.in_ack > self.last_rel_sent and self.reliable_r_ack != self.reliable_s :
		# 		send_reliable = True

		# 	if self.busy == False:
		# 		send_reliable = True
		# 		self.busy = True
		# 		self.reliable_s ^= 1
			


		# 	msg = bytearray(10)
		# 	self.reliable_s = 1
		# 	#print(self.in_seq,self.out_seq)
		# 	struct.pack_into('<I',msg,0,(self.out_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_s<<31))
		# 	struct.pack_into('<I',msg,4,(self.in_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_r<<31))
		# 	struct.pack_into('<H',msg,8,self.qport)

		# 	msg += data
		# 	ba = msg
		# 	self.out_seq +=1

		# 	if send_reliable == True:
		# 		self.last_rel_sent = self.out_seq
			
		# else:
		# 	ba = b'\xFF\xFF\xFF\xFF' + data
		

		if rel:
			self.out_seq += 1
			msg = bytearray(10)
			# print(f"reliable_s is {self.reliable_s}")
			# print(f"reliable_r is {self.reliable_r}")
			struct.pack_into('<I',msg,0,(self.out_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_s<<31))
			struct.pack_into('<I',msg,4,(self.in_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_r<<31))
			struct.pack_into('<H',msg,8,self.qport)
			ba = msg + data
		else:
			ba = b'\xFF\xFF\xFF\xFF' + data


		#print("sending {} : ".format(len(ba)),":".join("{0:x}".format(ord(c)) for c in ba.decode('ISO 8859-1')),"\n")
		# print(f"sending... {len(ba)}")
		# print( ":".join("{0:x}".format(c) for c in ba))
		self.s.sendto(ba,self.server)


	def recv(self):
		global last_packet_stamp
		while True:
			msg = bytearray(1400)
			view = memoryview(msg)
			try:
				nbytes = self.s.recv_into(view)
			except socket.error as e:
				err = e.args[0]
				if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
					return False
				print("Network Error")
				sys.exit(1)
			last_packet_stamp = time.time()
			view = view[:nbytes]

			# print("received {} : ".format(nbytes),":".join("{0:x}".format(ord(c)) for c in bytes(view).decode('ISO 8859-1')),"\n")
			# print("received: ",bytes(view),"\n")
			# print("received: ",bytes(view).decode('ISO 8859-1'),"\n")

			s=struct.unpack_from('<i',view,0)
			if s[0] == -1:
				# connectionless packet ?
				# print("[UNCONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				return view[4:]
			else:
				# print("[CONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				pass


			#so must be connected packet...
			self.in_seq = struct.unpack_from('<I',view,0)[0]
			view = view[4:]
			reliable_message = self.in_seq >> 31

			
			if reliable_message :
				self.reliable_r ^= 1

			# turn off last bit
			self.in_seq = self.in_seq & ~(1<<31)
			# s=struct.unpack_from('<i',view,0)
			view = view[4:]
			# reliable_ack = s[0] >> 31
			# self.in_ack = s[0] & ( ~(1<<31) & 0xFFFFFFFF ) #off reliable bit
			

			# if in_seq <= self.in_seq :
			# 	return

			# if reliable_ack == self.reliable_s:
			# 	#make way for new reliable // clear length
			# 	self.busy = False

			# self.in_seq = in_seq
			# self.in_ack = in_ack
			# self.reliable_r_ack = reliable_ack
			
			
				# if ( *(int *)rcv_buf == -1 ) {
				# 	printf("connectionless packet!\n");
				# 	return;
				# }
				# in_seq = *(unsigned int*)&rcv_buf[0];
			 #  //printf("fuck %08X %u\n",in_seq,in_seq);
				# i_reliable = in_seq >> 31;

				# if ( i_reliable ) {
				# 	i_recvreliable ^= 1; // marker
				# }

				# in_seq &= ~(1<<31); //off reliable bit

			 #  //printf("in_Seq is %u\n",in_seq);
				# p = &rcv_buf[8];

			#command byte

			# there are many commands inside 1 packet
			# if you cannot parse 1 packet, you can't parse the others.
			while view:
				# print(view.nbytes)
				cmd = struct.unpack_from('<B',view,0)[0]
				# print(f"---------PARSING PACKET : {packetIDtoName(cmd)}")
				view = view[1:]

				if cmd == 0x00: #nothing
					pass		
				if cmd == PACKET_SVC.SVC_DISCONNECT: #disconnect
					print("PACKET: disconnect\n")
					conn.connected = False
					conn.bot.lastServerFrame = -1
					conn.get_challenge()
					conn.connect()
					conn.out_seq = 0
					conn.in_seq = 0
					conn.reliable_s = 1
					conn.new()
				elif cmd == PACKET_SVC.SVC_PRINT: #print
					view=view[1:]
					s,view = self.pars.string(view)
					if s.tobytes().decode(('ISO 8859-1')) == "Server restarted\n":
						print("Server restart detected via print\n");
						conn.connected = False
						conn.bot.lastServerFrame = -1
						conn.get_challenge()
						conn.connect()
						conn.out_seq = 0
						conn.in_seq = 0
						conn.reliable_s = 1
						conn.new()
					print("PACKET: print\n",s.tobytes(),s.tobytes().decode('ISO 8859-1'))
				elif cmd == PACKET_SVC.SVC_NAMEPRINT:
					# 2 bytes and a string, 2nd byte = teamsay
					data1 = struct.unpack_from('<B',view,0)[0]
					view=view[1:]
					data2 = struct.unpack_from('<B',view,0)[0]
					view=view[1:]

					s,view = self.pars.string(view)
					s = s.tobytes().decode('ISO 8859-1')

					print(f"client {data1} says : {s}")

					s = s.split(']')[1].strip()
					if s.startswith("@sofgpt"):
						print(s)
						answer = gtp_ask(s,heartbeat)

						print(answer)
						self.send(True,(f"\x04say {answer}\x00").encode('ISO 8859-1'))
					
				elif cmd == PACKET_SVC.SVC_STUFFTEXT: #stufftext	
					s,view = self.pars.string(view)
					print("PACKET: stufftext\n",s.tobytes(),s.tobytes().decode('ISO 8859-1'))

					l=self.pars.stufftext(s,self)
					for a in l:
						if a.find("configstrings",0) == 0:
							
							self.send(True,("\x04"+a+"\x00").encode('ISO 8859-1'))
						elif a.find("begin",0) == 0:
							self.connected = True
							self.bot.init_timer()
							# send it back to server
							self.send(True,("\x04"+f"begin {self.bot.precache}"+"\x00").encode('ISO 8859-1'))

						elif a.find(".check",0) == 0:
							
							a = a.replace("#cl_minfps","5")
							a = a.replace("#cl_maxfps","30")

							a = a.replace("#gl_drawmode","0")
							a = a.replace("#gl_fogmode","0")
							a = a.replace("#gl_modulate","2")
							a = a.replace("#gl_lockpvs","0")
							a = a.replace("#gl_nobind","0")
							a = a.replace("#gl_driver","opengl32")
							a = a.replace("#gl_showtris","0")
							a = a.replace("#gl_drawflat","0")
							a = a.replace("#gl_dlightintensity","2")
							a = a.replace("#gl_nobind","0")
							a = a.replace("#r_nearclipdist","4")
							a = a.replace("#r_drawworld","1	")
							a = a.replace("#r_fullbright","0")

							a = a.replace("#ghl_shadow_dist","25")
							a = a.replace("#cl_testlights","0")
							a = a.replace("#cl_testblend","0")
							# send it back to server
							self.send(True,("\x04"+a+"\x00").encode('ISO 8859-1'))
						else:
							# send it back to server
							self.send(True,("\x04"+a+"\x00").encode('ISO 8859-1'))
						
				elif cmd == PACKET_SVC.SVC_SERVERDATA: #serverdata
					print("PACKET: serverdata\n")
					self.expectmapname = True
					view = view[9:]
					s,view = self.pars.string(view)
					self.bot.playernum = struct.unpack_from('<h',view,0)[0]
					view = view[2:]
					s,view = self.pars.string(view)
					self.bot.map = s.tobytes().decode("ISO 8859-1")

				elif cmd == PACKET_SVC.SVC_CONFIGSTRING: #configstring		
					#print("PACKET: configstring\n")
					view=view[2:]
					if view[0] == 0xFF and view[1] == 0xFF:
						s,view = self.pars.string(view)
					else:
						view=view[2:]
					
				elif cmd == PACKET_SVC.SVC_SPAWNBASELINE: #baseline
					# search for precache hm\
					data = view.tobytes()
					find_precache = data.find(b"\x0dprecache",0)
					if find_precache >= 0:
						self.bot.precache = int(data[find_precache+9:].split(b'\x0a',1)[0])
						print(f"acquired precache number : {self.bot.precache}\n")
						print (f"download {self.bot.mapname}.eal")
						self.send(True,("\x04"+f"download {self.bot.mapname}.eal"+"\x00").encode('ISO 8859-1'))
						self.i_downloading = 1
						print("SERVED BY BASELINE\n")
					else:
						print("failed getting precache\n")
					break;
					tmp2 = 0
					tmp = struct.unpack_from('<b',view,0)[0]
					view=view[1:]
					if tmp < 0:
						tmp = struct.unpack_from('<b',view,0)[0] << 8 | tmp
						view=view[1:]
					tmp2 = tmp
					if tmp2 < 0:
						tmp = struct.unpack_from('<b',view,0)[0] << 16 | tmp
						view=view[1:]
						tmp2 = tmp

					if tmp2 & 0x800000:
						tmp = struct.unpack_from('<b',view,0)[0] << 24 | tmp
						view=view[1:]
						tmp2 = tmp

					if tmp2 & 0x1000000:
						tmp3 = struct.unpack_from('<h',view,0)[0]
						view=view[2:]

					
					# delta_sequence
					tmp = struct.unpack_from('<l',view,0)[0]
					view=view[4:]
						
					# delta_entity
					tmp = struct.unpack_from('<h',view,0)[0]
					view=view[2:]

					# delta_flags
					delta_flags = struct.unpack_from('<b',view,0)[0]
					view=view[1:]
						
					if delta_flags & ENTITY_BITS:
						# this delta is for an entity
						delta_entity = MSG_ReadBits(read_buffer, MAX_EDICT_BITS)
						parsed_message['delta_entity'] = delta_entity

						# update the entity
						if delta_entity >= 0 and delta_entity < MAX_EDICTS:
							entities[delta_entity] = ParseDeltaEntity(read_buffer, entities[delta_entity])
						else:
							raise Exception("Invalid delta entity number")
					else:
						# this delta is for a client
						client_num = delta_entity - 1
						parsed_message['client_num'] = client_num

						if client_num >= MAX_CLIENTS:
							raise Exception("Invalid client number")

						# update the client state
						ParseDeltaClient(read_buffer, client_num, delta_flags, parsed_message)

						return parsed_message

				elif cmd == PACKET_SVC.SVC_DOWNLOAD: #download
					#print("PACKET: download\n")
					view=view[3:]

					if  self.i_downloading == 1:
						self.send(True,("\x04"+f"download maps/dm/{self.bot.mapname}.sp"+"\x00").encode('ISO 8859-1'))
						self.i_downloading += 1
					elif self.i_downloading == 2:
						self.send(True,("\x04"+f"download maps/dm/{self.bot.mapname}.wrs"+"\x00").encode('ISO 8859-1'))
						self.i_downloading += 1
					elif self.i_downloading == 3:
						self.send(True,("\x04"+f"sv_precache {self.bot.precache}"+"\x00").encode('ISO 8859-1'))
						self.i_downloading = 0;

				elif cmd == PACKET_SVC.SVC_FRAME: #frame
					# print("svc_Frame")
					self.bot.lastServerFrame = struct.unpack_from('<I',view,0)[0]
					# print(f"received frame = {self.bot.lastServerFrame}")
					view=view[4:]
					view=view[4:]
					view=view[4:]
					areabits = struct.unpack_from('<B',view,0)[0]
					view=view[1:]
					view=view[areabits:]
					cmd = struct.unpack_from('<B',view,0)[0]
					view=view[1:]

					# readPlayerState
					flags = struct.unpack_from('<I',view,0)[0]
					view=view[4:]
					if flags & PS_GUN:
						view=view[2:]
						view=view[1:]
					if flags & PS_GUN_CLIP:
						view=view[1:]
					if flags & PS_GUN_AMMO:
						view=view[2:]
					if flags & PS_GUN_RELOAD:
						view=view[1:]
					if flags & PS_RESTART_COUNT:
						view=view[1:]
					if flags & PS_BUTTONS_INHIBIT:
						view=view[1:]
					if flags & PS_BOD:
						view=view[2:]
					if flags & PS_M_TYPE:
						view=view[1:]
					if flags & PS_M_ORIGIN:
						view=view[2:]
						view=view[2:]
						view=view[2:] 
					if flags & PS_M_VELOCITY:
						view=view[2:]
						view=view[2:]
						view=view[2:]
					if flags & PS_M_TIME:
						view=view[1:]
					if flags & PS_M_FLAGS:
						view=view[1:]
					if flags & PS_M_GRAVITY:
						view=view[2:]
					if flags & PS_M_DELTA_ANGLES:
						view=view[2:]
						view=view[2:]
						view=view[2:]
					if flags & PS_M_movESCALE:
						view=view[1:]
					if flags & PS_VIEWOFFSET:
						view=view[1:]
						view=view[1:]
						view=view[1:]
					if flags & PS_VIEWANGLES:
						view=view[2:]
						view=view[2:]
						view=view[2:]
					if flags & PS_REMOTE_VIEWANGLES:
						view=view[2:]
						view=view[2:]
						view=view[2:]
					if flags & PS_REMOTE_VIEWORIGIN:
						view=view[2:]
						view=view[2:]
						view=view[2:]
					if flags & PS_REMOTE_ID:
						view=view[1:]
						view=view[1:]
					if flags & PS_KICKANGLES:
						view=view[1:]
						view=view[1:]
						view=view[1:]
					if flags & PS_WEAPONKICKANGLES:
						view=view[1:]
					if flags & PS_BLEND:
						view=view[1:]
						view=view[1:]
						view=view[1:]
						view=view[1:]
					if flags & PS_FOV:
						view=view[1:]
					if flags & PS_RDFLAGS:
						view=view[1:]

					# Long
					statbits = struct.unpack_from('<i',view,0)[0]
					view=view[4:]
					
					#ParseStats
					for k in range(16):
						if ( statbits & ( 1<<k) ):
							view=view[2:]

					if flags & PS_CINEMATICFREEZE:
						view=view[1:]
					if flags & PS_MUSICID:
						view=view[1:]
					if flags & PS_AMBSOUNDID:
						view=view[2:]
					if flags & PS_DMRANK:
						view=view[1:]
						view=view[1:]
					if flags & PS_SPECTATORID:
						view=view[1:]

					
					cmd = struct.unpack_from('<B',view,0)[0]
					view=view[1:]

					# readEntities
					skinnum = 100;
					newnum = 0;
					entitycount = 0;
					while 1:
						skinnum = 100;
						flags = struct.unpack_from('<B',view,0)[0]
						view=view[1:]

						if flags & U_MOREBITS1:
							flags |= struct.unpack_from('<B',view,0)[0] << 8;
							view=view[1:]
						if flags & U_MOREBITS2:
							flags |= struct.unpack_from('<B',view,0)[0] << 16;
							view=view[1:]
						if flags & U_MOREBITS3:
							flags |= struct.unpack_from('<B',view,0)[0] << 24;
							view=view[1:]
						if flags & U_NUMBER16:
							newnum = struct.unpack_from('<h',view,0)[0]
							view=view[2:]
						else:
							newnum = struct.unpack_from('<B',view,0)[0]
							view=view[1:]
						if not newnum:
							break
						entitycount += 1

						if flags & U_MODEL:
							view=view[1:]
						if flags & U_RENDERMODEL:
							view=view[1:]
						if flags & U_FRAME8:
							view=view[1:]
						if flags & U_FRAME16:
							view=view[2:]
						if ( flags & (U_SKIN8|U_SKIN16) ) == (U_SKIN8|U_SKIN16):
							skinnum = struct.unpack_from('<i',view,0)[0]
							view=view[4:]
						elif flags & U_SKIN8:
							skinnum = struct.unpack_from('<b',view,0)[0]
							view=view[1:]
						elif flags & U_SKIN16:
							skinnum = struct.unpack_from('<h',view,0)[0]
							view=view[2:]
						if (flags & (U_EFFECTS8|U_EFFECTS16) ) == (U_EFFECTS8|U_EFFECTS16):
							view=view[4:]
						elif flags & U_EFFECTS8:
							view=view[1:]
						elif flags & U_EFFECTS16:
							view=view[2:]

						if ( flags & (U_RENDERFX8|U_RENDERFX16) ) == (U_RENDERFX8|U_RENDERFX16):
							view=view[4:]
						elif flags & U_RENDERFX8:
							view=view[1:]
						elif flags & U_RENDERFX16:
							view=view[2:]
						if flags & U_ORIGIN1:
							view=view[2:]
						if flags & U_ORIGIN2:
							view=view[2:]
						if flags & U_ORIGIN3:
							view=view[2:]
						if flags & U_ANGLE1:
							view=view[1:]
						if flags & U_ANGLE2:
							view=view[1:]
						if flags & U_ANGLEDIFF:
							view=view[1:]
						if flags & U_ANGLE3:
							view=view[1:]
						if flags & U_SOUND:
							view=view[1:]
							view=view[1:]
						if flags & U_EVENT:
							c = struct.unpack_from('<b',view,0)[0]
							view=view[1:]
							view=view[1:]
							if c < 0:
								c = struct.unpack_from('<b',view,0)[0]
								view=view[1:]
								view=view[1:]
								if c < 0:
									c = struct.unpack_from('<b',view,0)[0]
									view=view[1:]
									view=view[1:]

						if flags & U_SOLID:
							if skinnum == self.bot.playernum:
								solid = struct.unpack_from('<i',view,0)[0]
							view=view[4:]
						if flags & U_EFFECT:
							x = struct.unpack_from('<h',view,0)[0]
							view=view[2:]
							for j in range(12):
								if x & (1<<j):
									view=view[2:]

				elif cmd == PACKET_SVC.SVC_GHOULRELIABLE: #ghoulstring reliable
					print("PACKET: ghoul reliable\n")
					size = struct.unpack_from('<h',view,0)[0]
					view = view[2:]
					view = view[size:]
				elif cmd == PACKET_SVC.SVC_GHOULUNRELIABLE:
					break
					pass
				else:
					print(f"PACKET: {packetIDtoName(cmd)} \n")
					# fetch new packet ( SKIPS LOTS OF DATA )
					break

			# endwhile
			if self.expectmapname:
				# print("FINDING MAP NAME")
				# "maps/dm/"

				pos = msg.find(b"maps/dm/",0)
				if pos >= 0:
					self.bot.mapname = msg[pos:].split(b'.',1)[0].decode("ISO 8859-1")
					print (self.bot.mapname)
					self.expectmapname = False
		return True
			
	def end(self):
		self.s.close

PS_M_TYPE = (1<<0)
PS_M_ORIGIN = (1<<1)
PS_M_VELOCITY = (1<<2)
PS_M_TIME = (1<<3)
PS_M_FLAGS = (1<<4)
PS_M_GRAVITY = (1<<5)
PS_M_DELTA_ANGLES = (1<<6)
PS_VIEWOFFSET = (1<<7)

PS_VIEWANGLES = (1<<8)
PS_KICKANGLES = (1<<9)
PS_BLEND = (1<<10)
PS_FOV = (1<<11)
PS_REMOTE_VIEWORIGIN = (1<<12)
PS_REMOTE_ID = (1<<13)
PS_RDFLAGS = (1<<14)
PS_REMOTE_VIEWANGLES = (1<<15)

PS_GUN = (1<<16)
PS_GUN_CLIP = (1<<17)
PS_GUN_AMMO = (1<<18)
PS_WEAPONKICKANGLES = (1<<19)
PS_BOD = (1<<20)
PS_PIV = (1<<21)
PS_CINEMATICFREEZE = (1<<22)
PS_MUSICID = (1<<23)

PS_AMBSOUNDID = (1<<24)
PS_DMRANK = (1<<25)
PS_SPECTATORID = (1<<26)
PS_M_movESCALE = (1<<27)
PS_RESTART_COUNT = (1<<28)
PS_BUTTONS_INHIBIT = (1<<29)
PS_GUN_RELOAD = (1<<30)

U_ORIGIN1 = (1<<0)
U_ORIGIN2 = (1<<1)
U_ANGLE2 = (1<<2)
U_ANGLE3 = (1<<3)
U_ANGLE1 =  (1<<4)
U_ORIGIN3 = (1<<5)
U_EVENT = (1<<6)
U_MOREBITS1 = (1<<7)

U_RENDERFX16 = (1<<8)
U_RENDERMODEL = (1<<9)
U_RENDERFX8 = (1<<10)
U_REmovE = (1<<11)
U_FRAME16 = (1<<12)
U_EFFECT = (1<<13)
U_EFFECTS16 = (1<<14)
U_MOREBITS2 = (1<<15)


U_EFFECTS8= (1<<16)
U_FRAME8= (1<<17)
U_SOLID=  (1<<18)
U_SKIN8=  (1<<19)
U_MODEL=  (1<<20)
U_SOUND=  (1<<21)
U_SOUND_HI= (1<<22)
U_MOREBITS3=(1<<23)


U_NUMBER16 =  (1<<24)
U_SKIN16 =  (1<<25)
U_ANGLEDIFF = (1<<26)

BUTTON_ATTACK=1
BUTTON_USE=2
BUTTON_ALTATTACK=4
BUTTON_WEAP3=8
BUTTON_WEAP4=16
BUTTON_RUN=32
BUTTON_ACTION=64
#define BUTTON_ANY      128     // any key whatsoever

yaw = 2047;
roll = 0;
pitch = 2048; # 0 = look flat //  2047 = down_max // 2048 = up_max

one = bytes((1,))
zero = bytes((0,))

lookup = True
lookdown = False
right = True
left = False
back = False
forward = False
moveup = False
movedown = False
leanleft = False
leanright = False
shoot = False
moveleft = False
moveright = False
def oneDeltaUsercmd(ba_buf, mode):
	global yaw,roll,pitch
	buttons = bytes((BUTTON_ATTACK,))
	d = bytearray(4)
	# PITCH_ANGLE -2047 -> 2047 AKA 0 -> 4095
	# 
	# **************************PITCH*********************************
	# 
	if lookup:
		pitch -= 1;
		if pitch == -1:
			pitch = 4095
	elif lookdown:
		pitch += 1;
		if pitch == 4096:
			pitch = 0
	dataToBits(ba_buf,one,1)

	
	struct.pack_into('<H',d,0,pitch)
	dataToBits(ba_buf,d,12)

	
	# /*
	# **************************YAW*********************************
	# */
	if right:
		yaw -= 1;
		if yaw == -1:
			yaw = 4095
	elif left:
		yaw += 1;
		if yaw == 4096:
			yaw = 0
	dataToBits(ba_buf,one,1)
	# crouch_test = ANGLE2SHORT12(-90);
	struct.pack_into('<H',d,0,yaw)
	dataToBits(ba_buf,d,12)
	
	# 
	# **************************ROLL*********************************
	# */
	# ROLL_ANGLE  -2047 -> 2047 AKA 0 -> 4095
	# dataToBits(buf,&zero,1);
	dataToBits(ba_buf,one,1)
	struct.pack_into('<H',d,0,roll)
	dataToBits(ba_buf,d,12)


	# 
	# **************************FORWARDMOVE*********************************
	# 
	if back:
		
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(100))
		dataToBits(ba_buf,d,10)
	elif forward:
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(-100))
		dataToBits(ba_buf,d,10)
	else:
		dataToBits(ba_buf,zero,1)
	
	# /*
	# **************************SIDEMOVE*********************************
	# */
	if moveleft:
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(-100))
		dataToBits(ba_buf,d,10)
	elif moveright:
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(100))
		dataToBits(ba_buf,d,10)
	else:
		dataToBits(ba_buf,zero,1)

	# /*
	# **************************UPMOVE*********************************
	# */

	if moveup:
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(100))
		dataToBits(ba_buf,d,10)
	elif movedown:
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(-100))
		dataToBits(ba_buf,d,10)
	else:
		# upmove requires this else the player doesnt obey gravity correctly glitch on spawn?
		dataToBits(ba_buf,one,1)
		struct.pack_into('<H',d,0,tenbit(0))
		dataToBits(ba_buf,d,10)

	# 
	# **************************BUTTONS*********************************
	# */
	# toggle shoot useful for respawning after death
	if mode:
		# print("ZERObefore is " + "".join("\\x{0:02x}".format(x) for x in ba_buf))
		dataToBits(ba_buf,zero,1)
		# print("ZEROafter is " + "".join("\\x{0:02x}".format(x) for x in ba_buf))
	else:
		# print("ONEBUTTONSbefore is " + "".join("\\x{0:02x}".format(x) for x in ba_buf))
		dataToBits(ba_buf,one,1)
		dataToBits(ba_buf,buttons,8)
		# print("ONEBUTTONSafter is " + "".join("\\x{0:02x}".format(x) for x in ba_buf))

	# /*
	# **************************LEAN*********************************
	# */
	
	if leanleft:
		dataToBits(ba_buf,one,1)
		dataToBits(ba_buf,zero,1)
	elif leanright:
		dataToBits(ba_buf,one,1)
		dataToBits(ba_buf,one,1)
	else:
		# careful of leaning on respawn bug?
		dataToBits(ba_buf,zero,1)
	
	# /*
	# **************************LIGHTLEVEL*********************************
	# */
	# lightlevel - used for visibility a.i of computer to target you?
	# dataToBits(buf,&zero,1);
	dataToBits(ba_buf,one,1)
	lightLevel = bytes((5,))
	dataToBits(ba_buf,lightLevel,5)

	# /*
	# **************************MSEC*********************************
	# */
	msec = bytes((20,))
	dataToBits(ba_buf,msec,8)
	# /*
	# **************************FIREVENT*********************************
	# */
	dataToBits(ba_buf,zero,1)
	# /*
	# **************************ALTFIREEVENT*********************************
	# */
	dataToBits(ba_buf,zero,1)


def tenbit(n):
	n = n * 0.01 * 510
	return int(n) + 510

def completeUserCommandBitBuffer(mode):
	global bitpos
	usercmd = bytearray(64)
	oneDeltaUsercmd(usercmd,mode)
	oneDeltaUsercmd(usercmd,mode)
	oneDeltaUsercmd(usercmd,mode)

	bytesWritten = int(bitpos/8)
	bitpos = 0
	
	# for ( int i = 0 ; i < bytesWritten; i++ )
	# {
	# printf("byte %i :: %02X\n",i,*(unsigned char*)(fillme+i));
	# }
	# printf("\n");
	return (bytesWritten,usercmd)


mode = False
# Refer to Cl_SendCmd
# MSG_WriteDeltaUsercmd
# move_command
# checksum_byte
# delta_compression(-1)/serverframe
# bits (byte)
# bytes (byte/(s))
# msec (byte)
# lightlevel (byte)
def heartbeat():
	global mode
	buffer2 = bytearray.fromhex('02 00 FF FF FF FF')
	

	# fill the 'buffer'
	written_bytes,written_buffer = completeUserCommandBitBuffer(mode);
	# print(f"Wrote {written_bytes}\n")

	buffer2 += written_buffer[:written_bytes]

	mode = not mode;


	# update lastServerFrame
	if conn.bot.lastServerFrame == -1:
		struct.pack_into('<i',buffer2,2,conn.bot.lastServerFrame);
	else:
		# print(f"lastServerFrame = {conn.bot.lastServerFrame}")
		# negative direction = older
		#positive = oldest
		trick_val = (conn.bot.lastServerFrame & 15) -2
		if trick_val > 15:
			trick_val -= 16
		if trick_val < 0:
			trick_val += 16
		trick_val += 16
		struct.pack_into('<I',buffer2,2,trick_val);
		# struct.pack_into('<I',buffer2,2,conn.bot.lastServerFrame);

	# length move_command and checksum byte ignored 6-2 = 4

	# byte *base, int length, int sequence
	blossom = COM_BlockSequenceCRCByte(buffer2[2:],conn.out_seq+1);
	# print(f'blossom is {blossom}\n')
	buffer2[1] = blossom
	# printf("%i\n",out_seq+1);
	# for (int i= 0; i < usercmdSize; i ++ ) {
	# printf("%02X ",(unsigned char)tmp_buf[6+i]);
	# }
	# printf("\n");
	
	# increases out_seq

	# print(f'sending {buffer2}\n')
	conn.send(True,buffer2);


# ------------------------------------BEGIN-----------------------------------------
# chktbl2_view = memoryview(chktbl2)

ip = sys.argv[1]
port = int(sys.argv[2])
name = sys.argv[3]
print(f"ip : {ip}\nport : {port}\nname : {name}")
# sys.exit(0)

bot = Bot(name)
conn = Connection(ip,port,bot)
					
conn.get_challenge()
conn.connect()
conn.out_seq = 0
conn.in_seq = 0
conn.reliable_s = 1
conn.new()
# Return the time in seconds since the epoch as a floating point number.
begintime = time.time()


# 0.02 of a second = 20ms = 50fps
frame_length = 0.02
framecount = 0
second_timer = before_cpu = time.time()

init = False
while 1:
	framecount += 1
	conn.recv()
	
	# print(f"{conn.bot.lastServerFrame} {last_packet_stamp}" )

	# sends heartbeat 50 times a second
	if conn.connected:
		if not init:
			init = True
			conn.send(True,(f"\x04say Hi interact with me using @sofgpt\x00").encode('ISO 8859-1'))
		# print('heartbeat!\n')
		heartbeat()


	# if a second has passed
	if time.time() - second_timer >= 1.0:
		# print(f"fps is {framecount}")
		if last_packet_stamp < second_timer:
			conn.connected = False
			conn.bot.lastServerFrame = -1
			conn.get_challenge()
			conn.connect()
			conn.out_seq = 0
			conn.in_seq = 0
			conn.reliable_s = 1
			conn.new()

		framecount = 0
		second_timer = time.time()

	# seconds for this frame
	exec_time = time.time() - before_cpu
	# too fast? sleep some
	if exec_time < frame_length:
		# sleep please
		time.sleep(frame_length-exec_time)

	before_cpu = time.time()
conn.end()