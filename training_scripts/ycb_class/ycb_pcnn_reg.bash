#!/bin/bash
SRC_DIR=$HOME/src/generic_pose/generic_pose/src/generic_pose
echo ${1}
python $SRC_DIR/training/class_posecnn_trainer.py \
    --log_dir '/home/bokorn/results/ycb_finetune/class/pcnn_mse_model_'${1} \
    --checkpoint_dir '/scratch/bokorn/results/ycb_finetune/class/pcnn_mse_model_'${1} \
    --benchmark_folder '/scratch/bokorn/data/benchmarks/ycb/YCB_Video_Dataset' \
    --renders_folder '/scratch/bokorn/data/benchmarks/ycb/YCB_Video_Dataset/base_renders/model_'${1}'/' \
    --random_render_offset \
    --render_proportion 1.0 \
    --target_object ${1} \
    --augmentation_probability 0.5 \
    --brightness_jitter 1.0 \
    --contrast_jitter 1.0 \
    --saturation_jitter 1.0 \
    --hue_jitter 0.25 \
    --max_translation 0.2 \
    --min_scale 0.8 \
    --max_scale 1.2 \
    --max_num_occlusions 3 \
    --min_occlusion_area 0.1 \
    --max_occlusion_area 0.3 \
    --rotate_image \
    --batch_size 16 \
    --falloff_angle 20.0 \
    --loss_type 'MSE'

