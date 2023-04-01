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
