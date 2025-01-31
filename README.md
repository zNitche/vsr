# vsr
video streaming relay


### How it works
![hla_diagram](docs/hla_diagram.png)

### Notes
```
ffmpeg -re -i test.mp4 -vcodec mjpeg -f mjpeg tcp://127.0.0.1:8989
```

```
ffplay tcp://127.0.0.1:9000
```
