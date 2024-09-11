import usb.core
import usb.util

# Найти устройство
dev = usb.core.find(idVendor=0x0b0e)

if dev is None:
    print("Устройство Jabra не найдено")
else:
    print("Устройство Jabra найдено")

    try:
        dev.set_configuration()
        cfg = dev.get_active_configuration()

        print("Ожидание данных от устройства...")

        while True:
            data = dev.read(cfg[(0, 0)][(usb.ENDPOINT_IN | 1)].bEndpointAddress, 1024)
            print("Получены данные: ", data)

    except Exception as e:
        print(f"Ошибка при взаимодействии с устройством: {e}")
