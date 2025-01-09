from vsr import Server


def main():
    server = Server(port=8989)

    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    main()
