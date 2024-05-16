export MODEL_NAME="stabilityai/stable-diffusion-xl-base-1.0"
export INSTANCE_DIR="saved_images"
export OUTPUT_DIR="lora-trained-xl"
export VAE_PATH="madebyollin/sdxl-vae-fp16-fix"

echo "model init"

RANDOM_NAME=$(openssl rand -base64 12 | tr -dc 'a-z0-9' | fold -w 10 | head -n 1)
echo $RANDOM_NAME

python3 train_dreambooth_lora_sdxl.py \
    --pretrained_model_name_or_path=$MODEL_NAME  \
    --instance_data_dir=$INSTANCE_DIR \
    --pretrained_vae_model_name_or_path=$VAE_PATH \
    --output_dir=$OUTPUT_DIR \
    --mixed_precision="fp16" \
    --instance_prompt="$RANDOM_NAME, 1 man, a photo of upper body" \
    --resolution=720 \
    --train_batch_size=1 \
    --gradient_accumulation_steps=4 \
    --learning_rate=1e-4 \
    --lr_scheduler="constant" \
    --lr_warmup_steps=0 \
    --max_train_steps=1000 \
    # --validation_prompt="shshshss, 1girl, a photo of upper body" \
    # --validation_epochs=25 \
    # --seed="0" \
    # --push_to_hub

python3 inference.py --class_name="$RANDOM_NAME" --gender="man"