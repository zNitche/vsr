from vsr.server import Server
import threading


def main():
    server = Server(port=8989)
    replay_server = Server(port=9000, broadcaster=server, broadcast=True)

    try:
        rst = threading.Thread(target=replay_server.run)

        rst.start()
        server.run()
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    main()
