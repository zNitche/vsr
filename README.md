# vsr
video streaming relay


### How it works
![hla_diagram](docs/hla_diagram.png)

1. `Camera/s` start MJPEG streaming to `Relay`.
2. `Relay` handshake with `Broadcaster/s`.
3. `Broadcaster` On client connected -> request data stream from `Relay`,
then send it to client.
4. `Broadcaster` On client disconnected -> if there is no client connected,
stop receiving data from `Relay`.

### Notes
```
ffmpeg -re -i test.mp4 -vcodec mjpeg -f mjpeg tcp://127.0.0.1:8989
```

```
ffplay tcp://127.0.0.1:9000
```
