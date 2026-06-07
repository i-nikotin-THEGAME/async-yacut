import aiohttp
import urllib.parse


class YandexDiskClient:
    """Клиент для работы с Яндекс Диском"""

    API_HOST = "https://cloud-api.yandex.net/"
    API_VERSION = "v1"
    REQUEST_UPLOAD_URL = f"{API_HOST}{API_VERSION}/disk/resources/upload"
    DOWNLOAD_LINK_URL = f"{API_HOST}{API_VERSION}/disk/resources/download"

    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": f"OAuth {token}"}

    def _encode_filename(self, filename):
        """Кодирует имя файла для использования в URL"""
        # Кодируем все спецсимволы
        return urllib.parse.quote(filename, safe="")

    async def get_upload_link(self, session, filename):
        """Получает ссылку для загрузки файла на Яндекс Диск"""
        encoded_filename = self._encode_filename(filename)
        path = f"/YaCut/{encoded_filename}"
        params = {"path": path, "overwrite": "true"}

        async with session.get(
                self.REQUEST_UPLOAD_URL,
                headers=self.headers,
                params=params) as response:
            if response.status == 200:
                data = await response.json()
                href = data.get("href")
                return href
            else:
                error_text = await response.text()
                raise Exception(
                    f"Ошибка получения ссылки для загрузки: {error_text}"
                )

    async def upload_file(self, session, file_content, filename):
        """Загружает файл на Яндекс Диск"""
        upload_url = await self.get_upload_link(session, filename)

        if not upload_url:
            raise Exception("Не удалось получить ссылку для загрузки")

        async with session.put(upload_url, data=file_content) as response:
            if response.status not in (201, 202):
                error_text = await response.text()
                raise Exception(f"Ошибка загрузки файла: {error_text}")

        return True

    async def get_download_link(self, session, filename):
        """Получает ссылку на скачивание файла"""
        encoded_filename = self._encode_filename(filename)
        path = f"/YaCut/{encoded_filename}"
        params = {"path": path}

        async with session.get(
                self.DOWNLOAD_LINK_URL,
                headers=self.headers,
                params=params) as response:
            if response.status == 200:
                data = await response.json()
                download_url = data.get("href")
                if download_url:
                    download_url = urllib.parse.unquote(download_url)
                return download_url
            else:
                error_text = await response.text()
                raise Exception(
                    f"Ошибка получения ссылки для скачивания: {error_text}"
                )

    async def upload_and_share(self, file_content, filename):
        """Загружает файл и возвращает ссылку для скачивания"""
        async with aiohttp.ClientSession() as session:
            await self.upload_file(session, file_content, filename)
            download_link = await self.get_download_link(session, filename)
            return download_link
