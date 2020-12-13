# Side-Project 3 可疑IP視覺化(ipblacklist_map)

網路上某些資安部落格每日會更新ip黑名單列表(可能是攻擊來源or跳板)

根據這些ip清單繪製成世界地圖，進行統計分析

系統流程: 

Server(樹梅派)每日會跑cronjob，若ip black list更新，會將清單載回本機存入influxdb

藉由python模組geoip2將ip轉換成所在國家(geoip2是個很好用的東西...)，最後用grafana將資料視覺化

![alt tag](https://imgur.com/IjzfmQw.jpg)

![alt tag](https://imgur.com/9vNScNu.jpg)

![alt tag](https://imgur.com/70VzP2I.jpg)

![alt tag](https://imgur.com/So2hVaO.jpg)
