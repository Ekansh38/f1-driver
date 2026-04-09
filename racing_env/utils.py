import config

def get_human_action(keys):
    action = {"up": False, "down": False, "left": False, "right": False, "brake": False}
    for scheme_name in config.ACTIVE_CONTROLS:
        scheme = config.CONTROLS[scheme_name]
        for key in action:
            if keys[scheme[key]]:
                action[key] = True
    return action
