from diffusers import DiffusionPipeline, StableDiffusionXLImg2ImgPipeline
import torch
import os
import argparse

# 파서 생성
parser = argparse.ArgumentParser(description="Print a random name passed as an argument.")
# 'class_name' 인자 추가
parser.add_argument('--class_name', type=str, help='The random name to print.')
parser.add_argument('--gender', type=str, help='gender.')
# 인자 분석
args = parser.parse_args()

model = "stabilityai/stable-diffusion-xl-base-1.0"
pipe = DiffusionPipeline.from_pretrained(
model,
torch_dtype=torch.float16,
)
pipe.to("cuda")
pipe.load_lora_weights("lora-trained-xl/pytorch_lora_weights.safetensors")
refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
"stabilityai/stable-diffusion-xl-refiner-1.0",
torch_dtype=torch.float16,
)
refiner.to("cuda")

# prompt = "A picture of a hyewon kang, 1 girl, upper body"
prompt = "A picture of a {args.class_name}, 1 {args.gender}, upper body, wearing white shirts, high quality, photo realistic, 8k, profile, natural, look at camera, vivid"
negative_prompt = "ugly, deformed, noisy, blurry, distorted, grainy, text, cropped"
generator = torch.Generator("cuda").manual_seed(43)

# Run inference.
# image = pipe(prompt=prompt, output_type="latent", generator=generator).images[0]
# image = refiner(prompt=prompt, image=image[None, :], generator=generator).images[0]
# image.save("refined_sks_dog.png")

image = pipe(prompt=prompt, negative_prompt=negative_prompt, generator=generator, num_inference_steps=40)
image = image.images[0]
image = refiner(prompt=prompt, negative_prompt=negative_prompt, generator=generator, image=image)
image = image.images[0]

filename='sample'
file_ext='.png'
output_path='output/%s%s' %(filename,file_ext)
uniq=1
while os.path.exists(output_path):
  output_path='output/%s(%d)%s' % (filename,uniq,file_ext)
  uniq+=1
image.save(output_path)
