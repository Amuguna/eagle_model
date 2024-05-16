#!/bin/sh

git clone https://github.com/huggingface/diffusers
cd diffusers
pip install -e .

cd examples/dreambooth
pip install -r requirements_sdxl.txt

pip install peft==0.10.0
