import util
import struct
from .parser_utils import string

def _process_sp_print_data(stringPackageId, stringPackageIndex, data, dataBytes, player):
	"""
	Common function to process and print sp_print_data based on stringPackageId and stringPackageIndex.
	This function handles the filtering and printing logic shared between svc_sp_print_data_1 and svc_sp_print_data_2.
	"""
	if stringPackageId == 0: #GENERAL
		if stringPackageIndex == 0:
			player.main.chat_ui.post(f"[GENERAL] Dropped a %s")
		elif stringPackageIndex == 1:
			player.main.chat_ui.post(f"[GENERAL] %p sank like a rock")
		elif stringPackageIndex == 2:
			player.main.chat_ui.post(f"[GENERAL] %p melted")
		elif stringPackageIndex == 3:
			player.main.chat_ui.post(f"[GENERAL] %p was squished")
		elif stringPackageIndex == 4:
			player.main.chat_ui.post(f"[GENERAL] %p cratered")
		elif stringPackageIndex == 5:
			player.main.chat_ui.post(f"[GENERAL] %p couldn't take it anymore")
		elif stringPackageIndex == 6:
			player.main.chat_ui.post(f"[GENERAL] %p got blown up")
		elif stringPackageIndex == 7:
			player.main.chat_ui.post(f"[GENERAL] %p crisped")
		elif stringPackageIndex == 8:
			player.main.chat_ui.post(f"[GENERAL] %p was deep fried")
		elif stringPackageIndex == 9:
			player.main.chat_ui.post(f"[GENERAL] %p tried to leave")
		elif stringPackageIndex == 10:
			player.main.chat_ui.post(f"[GENERAL] %p was gouged to death")
		elif stringPackageIndex == 11:
			player.main.chat_ui.post(f"[GENERAL] %p was chomped by a dog")
		elif stringPackageIndex == 12:
			player.main.chat_ui.post(f"[GENERAL] %p shouldn't play with phosphorus grenades")
		elif stringPackageIndex == 13:
			player.main.chat_ui.post(f"[GENERAL] %p blew herself up")
		elif stringPackageIndex == 14:
			player.main.chat_ui.post(f"[GENERAL] %p blew himself up")
		elif stringPackageIndex == 15:
			player.main.chat_ui.post(f"[GENERAL] %p tripped on her own C4")
		elif stringPackageIndex == 16:
			player.main.chat_ui.post(f"[GENERAL] %p tripped on his own C4")
		elif stringPackageIndex == 17:
			player.main.chat_ui.post(f"[GENERAL] %p should stay away from live claymores")
		elif stringPackageIndex == 18:
			player.main.chat_ui.post(f"[GENERAL] %p melted her own brain")
		elif stringPackageIndex == 19:
			player.main.chat_ui.post(f"[GENERAL] %p melted his own brain")
		elif stringPackageIndex == 20:
			player.main.chat_ui.post(f"[GENERAL] %p killed herself")
		elif stringPackageIndex == 21:
			player.main.chat_ui.post(f"[GENERAL] %p killed himself")
		elif stringPackageIndex == 22:
			player.main.chat_ui.post(f"[GENERAL] %p was slashed open by %p")
		elif stringPackageIndex == 23:
			player.main.chat_ui.post(f"[GENERAL] %p was impaled by %p")
		elif stringPackageIndex == 24:
			player.main.chat_ui.post(f"[GENERAL] %p was blasted by %p's piece")
		elif stringPackageIndex == 25:
			player.main.chat_ui.post(f"[GENERAL] %p was hollow pointed by %p's monster magnum")
		elif stringPackageIndex == 26:
			player.main.chat_ui.post(f"[GENERAL] %p was perforated by %p's machine pistol")
		elif stringPackageIndex == 27:
			player.main.chat_ui.post(f"[GENERAL] %p was assaulted by %p's SMG")
		elif stringPackageIndex == 28:
			player.main.chat_ui.post(f"[GENERAL] %p was sniped by %p")
		elif stringPackageIndex == 29:
			player.main.chat_ui.post(f"[GENERAL] %p was sawn in half by %p's slugthrower")
		elif stringPackageIndex == 30:
			player.main.chat_ui.post(f"[GENERAL] %p was peppered by %p's shotgun")
		elif stringPackageIndex == 31:
			player.main.chat_ui.post(f"[GENERAL] %p was machinegunned by %p")
		elif stringPackageIndex == 32:
			player.main.chat_ui.post(f"[GENERAL] %p was popped by %p's phosphorus grenade")
		elif stringPackageIndex == 33:
			player.main.chat_ui.post(f"[GENERAL] %p ate %p's rocket")
		elif stringPackageIndex == 34:
			player.main.chat_ui.post(f"[GENERAL] %p almost dodged %p's rocket")
		elif stringPackageIndex == 35:
			player.main.chat_ui.post(f"[GENERAL] %p was microwaved by %p's MPG")
		elif stringPackageIndex == 36:
			player.main.chat_ui.post(f"[GENERAL] %p was flame broiled by %p")
		elif stringPackageIndex == 37:
			player.main.chat_ui.post(f"[GENERAL] %p tasted %p's hot napalm injection")
		elif stringPackageIndex == 38:
			player.main.chat_ui.post(f"[GENERAL] %p didn't see %p's C4")
		elif stringPackageIndex == 39:
			player.main.chat_ui.post(f"[GENERAL] %p found a claymore planted by %p")
		elif stringPackageIndex == 40:
			player.main.chat_ui.post(f"[GENERAL] %p's brain was melted by %p's neural grenade")
		elif stringPackageIndex == 41:
			player.main.chat_ui.post(f"[GENERAL] %p tried to get too intimate with %p")
		elif stringPackageIndex == 42:
			player.main.chat_ui.post(f"[GENERAL] %p died")
		elif stringPackageIndex == 43:
			player.main.chat_ui.post(f"[GENERAL] *")
		elif stringPackageIndex == 44:
			player.main.chat_ui.post(f"[GENERAL] client_sb %hd %hd %hu %hd %hu %hu")
		elif stringPackageIndex == 45:
			player.main.chat_ui.post(f"[GENERAL] team_sb %hd %hd %hu %hd")
		elif stringPackageIndex == 46:
			player.main.chat_ui.post(f"[GENERAL] %p fell on his own grenade")
		elif stringPackageIndex == 47:
			player.main.chat_ui.post(f"[GENERAL] %p fell on her own grenade")
		elif stringPackageIndex == 48:
			player.main.chat_ui.post(f"[GENERAL] %p was blown to bits by %p")
		elif stringPackageIndex == 49:
			player.main.chat_ui.post(f"[GENERAL] Spectator password incorrect")
		elif stringPackageIndex == 50:
			player.main.chat_ui.post(f"[GENERAL] Server spectator limit is full")
		elif stringPackageIndex == 51:
			player.main.chat_ui.post(f"[GENERAL] Password incorrect")
		elif stringPackageIndex == 52:
			player.main.chat_ui.post(f"[GENERAL] %p has moved to the sidelines")
		elif stringPackageIndex == 53:
			player.main.chat_ui.post(f"[GENERAL] %p joined the game")
		elif stringPackageIndex == 54:
			player.main.chat_ui.post(f"[GENERAL] No other players to chase")
		elif stringPackageIndex == 55:
			player.main.chat_ui.post(f"[GENERAL] spect_sb %hd %hd %hu %hu %hu")
		elif stringPackageIndex == 56:
			player.main.chat_ui.post(f"[GENERAL] %p was smacked by %p's concussion grenade")
		elif stringPackageIndex == 57:
			player.main.chat_ui.post(f"[GENERAL] client_ctf_sb %hd %hd %hu %hd %hu %hu %hd")
		elif stringPackageIndex == 58:
			player.main.chat_ui.post(f"[GENERAL] %d POINTS")
		elif stringPackageIndex == 59:
			player.main.chat_ui.post(f"[GENERAL] Frag Limit of %hd frags hit.")
		elif stringPackageIndex == 60:
			player.main.chat_ui.post(f"[GENERAL] Time Limit of %hd minutes hit.")
		elif stringPackageIndex == 61:
			player.main.chat_ui.post(f"[GENERAL] %s has entered the game!")
		elif stringPackageIndex == 62:
			player.main.chat_ui.post(f"[GENERAL] Score: ")
		elif stringPackageIndex == 63:
			player.main.chat_ui.post(f"[GENERAL] Ping:   ")
		elif stringPackageIndex == 64:
			player.main.chat_ui.post(f"[GENERAL] Time:   ")
		elif stringPackageIndex == 65:
			player.main.chat_ui.post(f"[GENERAL] Spectator")
		elif stringPackageIndex == 66:
			player.main.chat_ui.post(f"[GENERAL] Flag Captures: ")
		elif stringPackageIndex == 67:
			player.main.chat_ui.post(f"[GENERAL] Control Score:")
		elif stringPackageIndex == 68:
			player.main.chat_ui.post(f"[GENERAL] Team Red")
		elif stringPackageIndex == 69:
			player.main.chat_ui.post(f"[GENERAL] Team Blue")
		elif stringPackageIndex == 70:
			player.main.chat_ui.post(f"[GENERAL] Control Score")
		elif stringPackageIndex == 71:
			player.main.chat_ui.post(f"[GENERAL] Cannot Change Teams when in a Force Join game.")
		elif stringPackageIndex == 72:
			player.main.chat_ui.post(f"[GENERAL] client_conq_sb %hd %hd %hu %hd %hu %hu ")
	elif stringPackageId == 3: #WEAPONS/ITEMS - items.sp
		if stringPackageIndex == 0:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] PLASTIQUE")
		elif stringPackageIndex == 1:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] FLASH PAK")
		elif stringPackageIndex == 2:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] NPE")
		elif stringPackageIndex == 3:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] NIGHTVSN")
		elif stringPackageIndex == 4:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] CLAYMORE")
		elif stringPackageIndex == 5:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] NONE")
		elif stringPackageIndex == 6:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a flash pak.")
		elif stringPackageIndex == 7:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a neural pulse grenade.")
		elif stringPackageIndex == 8:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some armor")
		elif stringPackageIndex == 9:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't wear any more armor.")
		elif stringPackageIndex == 10:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more flashpacks.")
		elif stringPackageIndex == 11:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more C4.")
		elif stringPackageIndex == 12:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some health")
		elif stringPackageIndex == 13:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] No more ammo for your %s")
		elif stringPackageIndex == 14:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Ammo is now %d for your %s...")
		elif stringPackageIndex == 15:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a knife.")
		elif stringPackageIndex == 16:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some 9mm ammo.")
		elif stringPackageIndex == 17:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some 12 gauge shells.")
		elif stringPackageIndex == 18:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some .44 ammo.")
		elif stringPackageIndex == 19:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some 5.56 ammo.")
		elif stringPackageIndex == 20:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a battery.")
		elif stringPackageIndex == 21:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some flamethrower gas.")
		elif stringPackageIndex == 22:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some NM-22 rockets.")
		elif stringPackageIndex == 23:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a .44 pistol.")
		elif stringPackageIndex == 24:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a 9mm pistol.")
		elif stringPackageIndex == 25:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a 9mm suppressed SMG.")
		elif stringPackageIndex == 26:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a 5.56 SMG.")
		elif stringPackageIndex == 27:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a 5.56 sniper rifle.")
		elif stringPackageIndex == 28:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a repeating slugthrower.")
		elif stringPackageIndex == 29:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a 12 gauge shotgun.")
		elif stringPackageIndex == 30:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a heavy machinegun.")
		elif stringPackageIndex == 31:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a M-1943 rocket launcher.")
		elif stringPackageIndex == 32:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a microwave pulse gun.")
		elif stringPackageIndex == 33:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up an L-32 flame gun.")
		elif stringPackageIndex == 34:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some C4.")
		elif stringPackageIndex == 35:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some light amplification goggles.")
		elif stringPackageIndex == 36:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a claymore mine.")
		elif stringPackageIndex == 37:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up some slugs.")
		elif stringPackageIndex == 38:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more knives.")
		elif stringPackageIndex == 39:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more 9mm ammo.")
		elif stringPackageIndex == 40:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more 12 gauge shells.")
		elif stringPackageIndex == 41:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more .44 ammo.")
		elif stringPackageIndex == 42:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more 5.56 ammo.")
		elif stringPackageIndex == 43:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more batteries.")
		elif stringPackageIndex == 44:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more gas canisters.")
		elif stringPackageIndex == 45:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more rockets.")
		elif stringPackageIndex == 46:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more slugs.")
		elif stringPackageIndex == 47:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more light amplification goggles.")
		elif stringPackageIndex == 48:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more Claymore mines.")
		elif stringPackageIndex == 49:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more neural grenades.")
		elif stringPackageIndex == 50:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more weapons. You need to drop some of your existing weapons first.")
		elif stringPackageIndex == 51:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a medkit.")
		elif stringPackageIndex == 52:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more medkits.")
		elif stringPackageIndex == 53:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] MEDKIT")
		elif stringPackageIndex == 54:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] GRENADE")
		elif stringPackageIndex == 55:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up a grenade.")
		elif stringPackageIndex == 56:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You can't carry any more grenades.")
		elif stringPackageIndex == 57:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] FLAG")
		elif stringPackageIndex == 58:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Picked up the oppositions Flag.")
		elif stringPackageIndex == 59:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] Returned your teams flag to base.")
		elif stringPackageIndex == 60:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You already have this weapon.")
		elif stringPackageIndex == 61:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] You are uninjured, medical attention not necessary.")
		elif stringPackageIndex == 62:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] .44 pistol")
		elif stringPackageIndex == 63:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] 9mm pistol")
		elif stringPackageIndex == 64:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] 9mm suppressed SMG")
		elif stringPackageIndex == 65:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] 5.56 SMG")
		elif stringPackageIndex == 66:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] repeating slugthrower")
		elif stringPackageIndex == 67:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] 12 gauge shotgun")
		elif stringPackageIndex == 68:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] heavy machinegun")
		elif stringPackageIndex == 69:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] M-1943 rocket launcher")
		elif stringPackageIndex == 70:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] microwave pulse gun")
		elif stringPackageIndex == 71:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] L-32 flame gun")
		elif stringPackageIndex == 73:
			player.main.chat_ui.post(f"[WEAPONS/ITEMS] 5.56 sniper rifle")
	elif stringPackageId == 17: #SOFPLUS
		if stringPackageIndex == 0:
			# slot == data[:4]
			slot_id = struct.unpack_from('<i',data,0)[0]
			name = util.mem_to_str(data[4:-1])
			player.main.chat_ui.post(f"[SOFPLUS] Incoming player [{slot_id}]: {name}")
			try:
				player.main.set_slot_name(slot_id, name)
			except Exception:
				pass
		elif stringPackageIndex == 1:
			player.main.chat_ui.post(f"[SOFPLUS] Disconnect [%d]")
		elif stringPackageIndex == 2:
			player.main.chat_ui.post(f"[SOFPLUS] Ping too high: %d")
		elif stringPackageIndex == 3:
			player.main.chat_ui.post(f"[SOFPLUS] %p was kicked for ping: %d")
		elif stringPackageIndex == 4:
			player.main.chat_ui.post(f"[SOFPLUS] FPS too high: %d\nLower cl_maxfps to %d")
		elif stringPackageIndex == 5:
			player.main.chat_ui.post(f"[SOFPLUS] %p was kicked for FPS: %d")
		elif stringPackageIndex == 6:
			player.main.chat_ui.post(f"[SOFPLUS] You're way over the speed limit: %d")
		elif stringPackageIndex == 7:
			player.main.chat_ui.post(f"[SOFPLUS] %p was kicked for speeding: %d")
		elif stringPackageIndex == 8:
			player.main.chat_ui.post(f"[SOFPLUS] CAMPER\n\nSomeone who stays in one spot without moving more than 2 inches, just to get kills or because he doesn't know how to play")
		elif stringPackageIndex == 9:
			player.main.chat_ui.post(f"[SOFPLUS] Userinfo flood protection")
		elif stringPackageIndex == 10:
			player.main.chat_ui.post(f"[SOFPLUS] Wave flood protection")
		elif stringPackageIndex == 11:
			player.main.chat_ui.post(f"[SOFPLUS] Command flood protection")
		elif stringPackageIndex == 12:
			player.main.chat_ui.post(f"[SOFPLUS] Spectators are not allowed to do that")
		elif stringPackageIndex == 13:
			player.main.chat_ui.post(f"[SOFPLUS] Weapon drop not allowed")
		elif stringPackageIndex == 14:
			player.main.chat_ui.post(f"[SOFPLUS] Flag drop not allowed")
		elif stringPackageIndex == 15:
			player.main.chat_ui.post(f"[SOFPLUS] %p was kicked for not having a valid password")
		elif stringPackageIndex == 16:
			player.main.chat_ui.post(f"[SOFPLUS] Alternate attack has been disabled for this weapon")
		elif stringPackageIndex == 17:
			player.main.chat_ui.post(f"[SOFPLUS] Primary attack has been disabled for this weapon")
		elif stringPackageIndex == 18:
			player.main.chat_ui.post(f"[SOFPLUS] *xv -140 yv -80 string \"Health: %s; Armor: %s; Weapon: %s; Clip: %s; Ammo: %s\"")
		elif stringPackageIndex == 19:
			player.main.chat_ui.post(f"[SOFPLUS] Health: %s; Armor: %s; Weapon: %s; Clip: %s; Ammo: %s")
		elif stringPackageIndex == 20:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Unknown command '%s'")
		elif stringPackageIndex == 21:
			s,_ = string(data)
			ss,_ = string(_)
			player.main.chat_ui.post(f"[SOFPLUS] Timelimit: {util.mem_to_str(s)} (time remaining: {util.mem_to_str(ss)})")
		elif stringPackageIndex == 22:
			player.main.chat_ui.post(f"[SOFPLUS] cl_maxfps set to %d")
		elif stringPackageIndex == 23:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Usage: .fps <fps>\n              Where <fps> is 30 .. %d")
		elif stringPackageIndex == 24:
			player.main.chat_ui.post(f"[SOFPLUS] Forced to spectate by the server admin\n\nPress F10 to change")
		elif stringPackageIndex == 25:
			player.main.chat_ui.post(f"[SOFPLUS] Forced to play by the server admin\n\nPress F10 to change")
		elif stringPackageIndex == 26:
			player.main.chat_ui.post(f"[SOFPLUS] Forced to red team by the server admin\n\nPress F10 to change")
		elif stringPackageIndex == 27:
			player.main.chat_ui.post(f"[SOFPLUS] Forced to blue team by the server admin\n\nPress F10 to change")
		elif stringPackageIndex == 28:
			player.main.chat_ui.post(f"[SOFPLUS] Error: You're not allowed to speak")
		elif stringPackageIndex == 29:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Usage: say \"your text\"")
		elif stringPackageIndex == 30:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Chat string too long - truncated to 150 chars")
		elif stringPackageIndex == 31:
			player.main.chat_ui.post(f"[SOFPLUS] %p started a vote (type .yes or .no to vote)")
		elif stringPackageIndex == 32:
			player.main.chat_ui.post(f"[SOFPLUS] Vote %s: %s")
		elif stringPackageIndex == 33:
			player.main.chat_ui.post(f"[SOFPLUS] Vote %s: %d")
		elif stringPackageIndex == 34:
			player.main.chat_ui.post(f"[SOFPLUS] Vote %s")
		elif stringPackageIndex == 35:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 1 (DM)")
		elif stringPackageIndex == 36:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 2 (Assassin)")
		elif stringPackageIndex == 37:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 3 (Arsenal)")
		elif stringPackageIndex == 38:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 4 (CTF)")
		elif stringPackageIndex == 39:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 5 (Realistic)")
		elif stringPackageIndex == 40:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 6 (Control)")
		elif stringPackageIndex == 41:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 7 (CTB)")
		elif stringPackageIndex == 42:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 8 (Team DM)")
		elif stringPackageIndex == 43:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 9 (Team Realistic)")
		elif stringPackageIndex == 44:
			player.main.chat_ui.post(f"[SOFPLUS] Vote gametype: 10 (Red/Blue CTB)")
		elif stringPackageIndex == 45:
			player.main.chat_ui.post(f"[SOFPLUS] Vote kick: %d (%p)")
		elif stringPackageIndex == 46:
			player.main.chat_ui.post(f"[SOFPLUS] Vote for the next map (default: %s)")
		elif stringPackageIndex == 47:
			player.main.chat_ui.post(f"[SOFPLUS] Vote cancelled")
		elif stringPackageIndex == 48:
			player.main.chat_ui.post(f"[SOFPLUS] Vote failed: Not enough votes (%d of %d required)")
		elif stringPackageIndex == 49:
			player.main.chat_ui.post(f"[SOFPLUS] Vote failed (Yes: %d; No: %d)")
		elif stringPackageIndex == 50:
			player.main.chat_ui.post(f"[SOFPLUS] Vote success (Yes: %d; No: %d)")
		elif stringPackageIndex == 51:
			player.main.chat_ui.post(f"[SOFPLUS] Vote success: Changing map to %s")
		elif stringPackageIndex == 52:
			player.main.chat_ui.post(f"[SOFPLUS] %p voted YES")
		elif stringPackageIndex == 53:
			player.main.chat_ui.post(f"[SOFPLUS] %p voted NO")
		elif stringPackageIndex == 54:
			player.main.chat_ui.post(f"[SOFPLUS] %p voted %s")
		elif stringPackageIndex == 55:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote has been disabled")
		elif stringPackageIndex == 56:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s has been disabled")
		elif stringPackageIndex == 57:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote not yet allowed")
		elif stringPackageIndex == 58:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s does not exist")
		elif stringPackageIndex == 59:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s not allowed.\nAllowed commands:\n  .yes\n  .no")
		elif stringPackageIndex == 60:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s not allowed.\nAllowed command:\n  .vote map <mapname>")
		elif stringPackageIndex == 61:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s %s not allowed")
		elif stringPackageIndex == 62:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote %s %d not allowed")
		elif stringPackageIndex == 63:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote not needed. Server is already using that setting")
		elif stringPackageIndex == 64:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote not possible\nAt least %d players required")
		elif stringPackageIndex == 65:
			player.main.chat_ui.post(f"[SOFPLUS] Error: Vote not allowed\nAnother player with the same IP address already voted")
	elif stringPackageId == 10: #dm_ctf
		# used for flag caps,recoveries,scoreboard data
		pass
	elif stringPackageId == 12: #BOT
		if stringPackageIndex == 4:
			player.main.chat_ui.post(f"[BOTS] {util.mem_to_str(data[4:-1])} disconnected.")
	elif stringPackageId == 18: #SOFPLUS_CUSTOM
		if stringPackageIndex == 12 or stringPackageIndex == 13 : #highscores
			player.main.chat_ui.post(f"[SOFPLUS_CUSTOM] {util.mem_to_str(data)}")
	else:
		print(f"unknown stringPackageId: {stringPackageId} stringPackageIndex: {stringPackageIndex}")
