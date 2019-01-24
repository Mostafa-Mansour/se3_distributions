python ../../../src/generic_pose/training/pose_distance_trainer.py \
--results_dir '/home/bokorn/results/shapenet/distance/shapenet_exp_fo20_th25' \
--train_data_folder '/scratch/bokorn/data/renders/shapenet/train_0.pkl' \
--valid_class_folder '/scratch/bokorn/data/renders/shapenet/valid_class_0.pkl' \
--valid_model_folder '/scratch/bokorn/data/renders/shapenet/valid_model_0.pkl' \
--batch_size 32 \
--lr 0.00001 \
--model_type alexnet \
--log_every_nth 100 \
--falloff_angle 20.0 \
--rejection_thresh_angle 25.0 \
--loss_type 'exp' \
--weight_file '/home/bokorn/results/shapenet/distance/shapenet_exp_fo20_th25/2018-08-01_17-36-42/weights/checkpoint_246000.pth' 

