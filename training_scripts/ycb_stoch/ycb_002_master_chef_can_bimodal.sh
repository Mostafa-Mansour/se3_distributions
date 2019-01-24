python ../../src/generic_pose/training/finetune_ycb_trainer.py \
    --results_dir '/scratch/bokorn/results/ycb_finetune/002_master_chef_can/bimodal' \
    --benchmark_folder '/scratch/bokorn/data/benchmarks/ycb/YCB_Video_Dataset' \
    --target_object 1 \
    --weight_file '/home/bokorn/pretrained/distance/shapenet_exp_fo20_th25.pth' \
    --use_exact_render \
    --sampling_distribution 'lambda x: ((x-np.pi/2)/(np.pi/2))**2 + 1' \
    --batch_size 16 --uniform_prop 1.0 \
    --falloff_angle 20.0 --loss_type 'exp'
