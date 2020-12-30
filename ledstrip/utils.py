

def is_raspberrypi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except Exception:
        pass
    return False

#if __name__ == '__main__':
is_raspberry_pi = is_raspberrypi()