from vsr import Relay, Camera


def main():
    relay = Relay(port=8989)

    try:
        cam1 = Camera(name="cam_1", address="127.0.0.1")
        relay.add_camera(cam1)

        relay.run()
    except KeyboardInterrupt:
        relay.stop()


if __name__ == '__main__':
    main()
