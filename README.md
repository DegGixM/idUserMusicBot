# id User Music Bot

Sesli Sohbetlerde Müzik çalmak için bir Telegram UserBot.

ABD numarası kullanmanız önerilir.(gerçek numaranız askıya alınırsa sorumlu değilim.kullanın riski size aittir) taahhüd yok garanti yok
Riski size ait olmak üzere kullanın..

<b> Heroku'ya Dağıtın </b>
[![tamilbot logo](https://te.legra.ph/file/be559ace3fe2b387dec9a.jpg)](https://heroku.com/deploy?template=https://github.com/DegGixM/idUserMusicBot)
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/DegGixM/idUserMusicBot)

- Projeyi Heroku'ya dağıttıktan sonra çalışanı etkinleştirin
- userbot'un çalışıp çalışmadığını kontrol etmek için userbot hesabının kendisinden veya bağlantılarından `!ping`, `!uptime` veya `!sysinfo` gönderin.
- userbot hesabının kendisinden veya kişilerinden sesli sohbetin etkinleştirildiği bir grup sohbetine `!join` gönderin.

**Özellikler**

- Oynatma listesi, sıra
- Çalma listesinde yalnızca bir parça olduğunda bir parçayı döngüye al
- Çalma listesindeki ilk iki parçanın sesini otomatik olarak indirir
   pürüzsüz oynamayı sağlamak için
- Geçerli çalma parçasını otomatik olarak sabitleyin
- Sesin mevcut çalma konumunu göster

**Oyuncu Eklentisi Nasıl Kullanılır**

1. Kullanıcı robotunu başlatın
2. userbot hesabının kendisinden sesli sohbetin etkinleştirildiği bir grup sohbetine `!join` gönderin
    veya kişileri, userbot hesabını grup yöneticisi yaptığınızdan emin olun ve
    en azından aşağıdaki izinleri verin:
    - Mesajları sil
    - Sesli sohbetleri yönetin (isteğe bağlı)
3. Bir sesi sesli sohbette çalmaya başlamak için `/play` ile yanıtlayın, her
    grubun üyesi artık `/play`, `/current` ve `!help` gibi ortak komutları kullanabilir.
4. Daha fazla komut için `!help`i kontrol edin

**Komutlar**

Ana eklenti, aşağıdaki komut komutlarına ve yönetici komutlarına sahip olan 'vc.player'dır.
Botu başlattıktan sonra, userbot hesabından grup sohbetine izin veren bir sesli sohbete `!join` gönderin
kendisi veya kişileri ve ardından `/play` ve `/current` gibi ortak komutlar kullanılabilir olacaktır.
grubun her üyesine. daha fazla komutu kontrol etmek için `!help` gönderin.

- Mevcut sesli sohbetin grup üyelerine sunulan ortak komutlar
- / (eğik çizgi) veya ! (ünlem işareti)

| Ortak Komutlar | Açıklama |
|-----------------|------------------------------- -------------------------|
| /play | çalmak/sıraya almak veya çalma listesini göstermek için bir sesle yanıtlayın |
| /current   | geçerli parçanın geçerli çalma süresini göster |
| /repo    | userbot'un git deposunu göster |
| !help | komutlar için yardımı göster |

- Userbot hesabının kendisi ve kişileri tarafından kullanılabilen yönetici komutları
- ile başlar ! (ünlem işareti)

| Yönetici Komutları | Açıklama |
|----------------|-------------------------------- --|
| !skip [n] ... | mevcut Şarkıyı atla! |
| !join | mevcut grubun sesli sohbetine katıl |
| !leave   | mevcut sesli sohbetten ayrıl |
| !vc | hangi VC'nin katıldığını kontrol edin |
| !stop    | oynamayı bırak |
| !replay  oynat | baştan oyna |
| !clean  | kullanılmayan RAW PCM dosyalarını kaldırın |
| !pause  | oynatmayı duraklat |
| !resume  | oynamaya devam et |
| !mute      | VC kullanıcı robotunun sesini kapatın |
| !unmute | VC kullanıcı robotunun sesini açın |

- Yalnızca userbot hesabının kendisi tarafından kullanılabilen diğer eklentilerden gelen komutlar

| Eklenti | Komutlar | Açıklama |
|---------|----------|---------------------|
| ping    | !ping    | ping zamanını göster |
| uptime  | !uptime  | userbot çalışma süresini göster |
| sysinfo | !sysinfo | sistem bilgilerini göster |


## Çalıştırmak

İki yöntemden birini seçin ve userbot'u şununla çalıştırın:
`python userbot.py`, <kbd>CTRL+c</kbd> ile durdurun. Aşağıdaki örnek
'vc.player' ve 'ping' eklentisini kullanacağınızı varsayalım,
`api_id`, `api_hash` kendi değerinize.
