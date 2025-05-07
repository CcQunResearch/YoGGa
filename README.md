# YoGGa

Source code for YoGGa in paper: 

**Your Gateway to Global Audiences: Fully Autonomous and Duration Controllable Dialogue Translation with Segment-wise Preference Optimization**

## Run

The code can be run in the following command:

```shell script
bash train.sh
```

## Dependencies

- [pytorch](https://github.com/pytorch/pytorch) == 2.2.2

- [transformers](https://github.com/huggingface/transformers) == 4.43.4

## Folder Hierarchy

```
YOGGA
├─AudioSegmentation
├─ConstructDataset
│  └─info
├─DurationAlignment
│  ├─Config
│  ├─Data
│  ├─Main
│  └─Save
├─SegPOSampling
│  ├─info
│  ├─log
│  ├─raw
│  └─temp
└─SpeakerTurnDetection
    └─model_ckpt
```
