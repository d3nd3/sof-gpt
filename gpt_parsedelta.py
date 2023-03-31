def CL_ParseDelta(read_buffer):
    parsed_message = {}

    # read the delta sequence number
    delta_sequence = MSG_ReadLong(read_buffer)
    parsed_message['delta_sequence'] = delta_sequence

    # read the delta entity number
    delta_entity = MSG_ReadShort(read_buffer)
    parsed_message['delta_entity'] = delta_entity

    # read the delta flags
    delta_flags = MSG_ReadByte(read_buffer)
    parsed_message['delta_flags'] = delta_flags

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
