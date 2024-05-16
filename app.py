from flask import Flask, jsonify, make_response, request
import subprocess
import os
import base64
import time
import shutil

app = Flask(__name__)

is_idle = True
# 1) check idle

# GET https://[host]/v1/gen/checkidle (idle 인지 확인)

# Success : 
    
# idle : {idle:"true"} /w status 200
# busy : {idle:"false"} /w status 200
# Fail :
#     status 500

# ===========================================
@app.route('/v1/gen/checkidle', methods=['GET'])
def check_idle():
    global is_idle
    if is_idle:
        response = {'idle':"true"}
        return make_response(jsonify(response), 200)
    else:
        response = {'idle':"false"}
        return make_response(jsonify(response), 200)

# 2) infer

# POST https://[host]/v1/gen/infer (이미지 생성)

# {
#     "images": [encoded_base64_images.png]
# }

# Success: status 200
# Fail : status 500
    
# (-1) : 이미 실행 중일 때
# (-2) : 실행하고 5초 이내 실패

# ===========================================
@app.route('/v1/gen/infer', methods=['POST'])
def infer_model():
    global is_idle
    # 이미 실행 중일 경우
    if not is_idle:
        return make_response(jsonify({"error": "Already processing another request."}), 500, {'ErrorCode': -1})

    try:
        # idle 상태 탈출
        is_idle = False
        # 요청 처리 플래그 설정
        is_processing = True
        start_time = time.time()

        
        # 요청 데이터 검증
        data = request.get_json()
        if 'images' not in data:
            return jsonify({"error": "Missing 'images' field in request data."}), 400

        # 저장한 인풋 이미지 삭제
        directory = 'saved_images'
        try:
            # 디렉토리 존재 여부 확인
            if os.path.exists(directory):
                # 디렉토리와 내부 파일/서브디렉토리 삭제
                shutil.rmtree(directory)
                print(f'Directory "{directory}" has been removed successfully.')
            else:
                print(f'Directory "{directory}" does not exist.')
        except Exception as e:
            print(f'Failed to delete directory "{directory}". Reason: {e}')
            
        # 이미지 디코드 및 처리
        images = data['images']
        
        # 이미지 저장
        if not os.path.exists('saved_images'):
            os.makedirs('saved_images')
        for index, img in enumerate(images):
            image_data = base64.b64decode(img)
            image_path = f"saved_images/image_{index + 1}.png"
            with open(image_path, 'wb') as file:
                file.write(image_data)
        #0 man 1 woman       
        gender = data['gender']
        
        # 아웃풋 이미지 삭제
        file_path = 'output/sample.png'
        # 파일 존재 여부 확인
        if os.path.exists(file_path):
            # 파일 삭제
            os.remove(file_path)
            print(f'File "{file_path}" has been removed successfully.')
        else:
            print(f'File "{file_path}" does not exist.')
        # try:
        #     # 파일 존재 여부 확인
        #     if os.path.exists(file_path):
        #         # 파일 삭제
        #         os.remove(file_path)
        #         print(f'File "{file_path}" has been removed successfully.')
        #     else:
        #         print(f'File "{file_path}" does not exist.')
        # except Exception as e:
        #     print(f'Failed to delete file "{file_path}". Reason: {e}')
            
        # 모델 실행
        print("---run model---")
        # 모델 실행
        if data.get('gender', 0) == 0:
            cmd = "./train.sh"
        else:
            cmd = "./train_woman.sh"

        output_log = 'output.log'
        # 프로세스 시작, 출력을 output.log 파일에 리다이렉션
        with open(output_log, 'w') as f:
            process = subprocess.Popen([cmd], stdout=f, stderr=subprocess.STDOUT, shell=True)

        # 비동기로 프로세스 종료 확인
        def monitor_process(p):
            p.wait()  # 프로세스가 종료될 때까지 대기
            global is_idle
            is_idle = True
            print("Process finished, set is_idle to True.")

        # 스레드 시작
        from threading import Thread
        thread = Thread(target=monitor_process, args=(process,))
        thread.start()
        
        print("---model end---")

        # return output.png
        # output_path = 'output/sample.png'
        # if not os.path.exists(output_path):
        #     if (time.time() - start_time) < 5:
        #         is_idle = True
        #         return jsonify({"error": "Failed to process within 5 seconds."}), 500, {'ErrorCode': -2}
        # else:
        #     with open(output_path, "rb") as image_file:
        #         encoded_string = base64.b64encode(image_file.read())
        #         is_idle = True
        #         return jsonify({"image": encoded_string.decode('utf-8')}), 200
    
    except Exception as e:
        is_idle = True
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        # 요청 처리 완료
        print("successfully done")

    return jsonify({"message": "Image processed successfully."}), 200
    
# 3) finish

# GET https://[host]/v1/gen/checkidle (infer 라우터에서 실행한 프로세스가 끝났는지 확인)

# Success : status 200
    
# { finish: "true", image: (base64_encoded_image.png) } : 끝남
# { finish: "false"} : 진행 중
# Fail : status 500
    
# finish
@app.route('/v1/gen/finish', methods=['GET'])
def check_finish():
    global is_idle
    
    if is_idle:
        try:
            output_path = 'output/sample.png'
            with open(output_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                return jsonify({"finish": "true", "image": encoded_string.decode('utf-8')}), 200
        except Exception as e:
            return make_response("", 500)
    else:
        response = {'finish':"false"}
        return make_response(jsonify(response), 200)
    
    return make_response("", 500)
    
@app.route('/')
def test():
    return "hello"
    
app.run(host='0.0.0.0',port=7772, debug=True)