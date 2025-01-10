# vsr
video streaming relay


### Notes
```
ffmpeg -re -i test.mp4 -vcodec mjpeg -f mjpeg tcp://127.0.0.1:8989
```

```
ffplay tcp://127.0.0.1:9000
```
