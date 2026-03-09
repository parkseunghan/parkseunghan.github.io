import os
import re

# 1. 타겟 경로 및 제거할 문자열 설정 (Configuration)
# 주의: knock-on-til 폴더가 _posts 아래에 있다면 '_posts/knock-on-til'로 경로를 지정하십시오.
# 만약 블로그 최상위 루트에 있다면 'knock-on-til'로 지정해야 합니다.
TARGET_DIR = '_posts/knock-on-til' 
TAG_TO_REMOVE = '[Writeup] '

def sanitize_titles_targeted():
    # 타겟 폴더 검증 (Verification)
    if not os.path.exists(TARGET_DIR):
        print(f"[-] {TARGET_DIR} 경로(Path)를 찾을 수 없습니다. 경로 설정을 다시 확인하십시오.")
        return

    # 2. 지정된 폴더 내부 탐색 (Directory Traversal)
    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            if filename.endswith('.md') or filename.endswith('.markdown'):
                filepath = os.path.join(root, filename)

                # 3. 마크다운 파일 읽기 (File Read)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 4. 문자열 정제 로직 (Sanitization Logic)
                def clean_title(match):
                    original_title = match.group(1).strip()
                    
                    # 쌍따옴표 내부의 문자열을 추출하여 타겟 태그를 1회만 제거(Replace)
                    if original_title.startswith('"') and original_title.endswith('"'):
                        inner_text = original_title[1:-1]
                        cleaned_text = inner_text.replace(TAG_TO_REMOVE, "", 1).strip()
                        return f'title: "{cleaned_text}"'
                    else:
                        cleaned_text = original_title.replace(TAG_TO_REMOVE, "", 1).strip()
                        return f'title: "{cleaned_text}"'

                # 'title: ' 로 시작하는 줄 치환
                new_content = re.sub(r'^title:\s*(.*)$', clean_title, content, flags=re.MULTILINE)

                # 5. 변경 사항이 있을 때만 파일 덮어쓰기 (Conditional File Write)
                if content != new_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"[*] Cleaned: {filepath}")
                
    print(f"[+] {TARGET_DIR} 내부 파일들의 메타데이터 정제(Metadata Sanitization)가 완료되었습니다.")

if __name__ == '__main__':
    sanitize_titles_targeted()