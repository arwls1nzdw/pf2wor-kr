[유니티 번역기 설치해야함](https://gall.dcinside.com/mgallery/board/view/?id=pillarsofeternity&no=33734)

번역기 config.ini에 아래 설정해야 나레이터 텍스트 구분 가능함
```
[TextFrameworks]
EnableIMGUI=False
EnableUGUI=False
EnableNGUI=False
EnableTextMeshPro=False
EnableTextMesh=False
EnableFairyGUI=False
```

문자열 파일 위치
```
SteamLibrary\steamapps\common\Pathfinder Second Adventure\Wrath_Data\StreamingAssets\Localization
```

파일 종류
```
파일 뒤에 _en이 붙으면 대화문에 영문 병기 버전임.
영문 병기 기준은 github의 Act, Comp(동료 관련) 폴더 내 파일, 번역 이후 10글자 이상인 문자열.

enGB.json
  deepl + 수작업 수정

enGB-namu.json
  deepl + 수작업 수정 + 나무위키(덮어쓰기)

enGB-kingmaker.json
  deepl + 수작업 수정 + 킹메이커 한글패치
  덮어쓰기 조건 - String key 일치, 6글자 이상, 태그 제거 + 소문자화 이후 영문 앞 6글자가 일치
  태그가 UUID라 이 조건이면 같은 데이터일 확률 90%는 넘는다고 봄
  9500개 정도 적용됨

enGB-km+namu.json
  deepl + 수작업 수정 + 킹메이커 한글패치 + 나무위키(덮어쓰기)
  나무위키를 가장 마지막에 덮어쓰기 함

enGB-namu+km.json
  deepl + 수작업 수정 + 나무위키(덮어쓰기) + 킹메이커 한글패치
  킹메이커를 가장 마지막에 덮어쓰기 함
```