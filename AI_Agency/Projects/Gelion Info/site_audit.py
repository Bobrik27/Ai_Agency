import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# Настройка прокси
# ВНИМАНИЕ: Учетные данные прокси были удалены для безопасности
# proxies = {
#     'http': 'http://<username>:<password>@<proxy_host>:<proxy_port>',
#     'https': 'http://<username>:<password>@<proxy_host>:<proxy_port>'
# }

# Заголовки для имитации реального браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def check_page_load_time(url):
    """Проверка времени загрузки страницы"""
    try:
        start_time = time.time()
        # Прокси-настройки удалены для безопасности
        response = requests.get(url, headers=headers)
        load_time = time.time() - start_time
        return load_time, response.status_code
    except Exception as e:
        return None, str(e)

def analyze_seo_elements(soup):
    """Анализ SEO элементов"""
    seo_report = {}
    
    # Заголовок страницы
    title = soup.find('title')
    if title:
        seo_report['title'] = {
            'text': title.text.strip(),
            'length': len(title.text.strip())
        }
    else:
        seo_report['title'] = {'text': 'Не найден', 'length': 0}
    
    # Мета-описание
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        seo_report['description'] = {
            'content': description.get('content', ''),
            'length': len(description.get('content', ''))
        }
    else:
        seo_report['description'] = {'content': 'Не найдено', 'length': 0}
    
    # Ключевые слова
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords:
        seo_report['keywords'] = {
            'content': keywords.get('content', ''),
            'length': len(keywords.get('content', ''))
        }
    else:
        seo_report['keywords'] = {'content': 'Не найдено', 'length': 0}
    
    # Заголовки H1-H6
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    h3_tags = soup.find_all('h3')
    
    seo_report['headings'] = {
        'h1_count': len(h1_tags),
        'h1_text': [h.text.strip() for h in h1_tags],
        'h2_count': len(h2_tags),
        'h3_count': len(h3_tags)
    }
    
    return seo_report

def check_images_optimization(soup, base_url):
    """Проверка оптимизации изображений"""
    images = soup.find_all('img')
    img_report = {'total': len(images), 'optimized': 0, 'unoptimized': 0, 'missing_alt': 0}
    
    for img in images:
        alt_attr = img.get('alt', '')
        if not alt_attr:
            img_report['missing_alt'] += 1
        
        # Проверяем, есть ли атрибуты размеров или src
        src = img.get('src', '')
        if src:
            full_url = urljoin(base_url, src)
            try:
                # Проверяем размер изображения
                img_response = requests.head(full_url, headers=headers)
                content_length = img_response.headers.get('content-length')
                if content_length:
                    size_kb = int(content_length) / 1024
                    if size_kb < 200:  # Условие для "оптимизированного" изображения
                        img_report['optimized'] += 1
                    else:
                        img_report['unoptimized'] += 1
                else:
                    img_report['unoptimized'] += 1
            except:
                img_report['unoptimized'] += 1
    
    return img_report

def check_links_status(soup, base_url):
    """Проверка статуса ссылок"""
    links = soup.find_all('a', href=True)
    link_report = {'total': len(links), 'working': 0, 'broken': 0, 'external': 0}
    
    for link in links:
        href = link.get('href', '')
        full_url = urljoin(base_url, href)
        
        # Определяем, внутренняя или внешняя ссылка
        if urlparse(full_url).netloc != urlparse(base_url).netloc:
            link_report['external'] += 1
            continue
        
        try:
            link_response = requests.head(full_url, headers=headers)
            if link_response.status_code < 400:
                link_report['working'] += 1
            else:
                link_report['broken'] += 1
        except:
            link_report['broken'] += 1
    
    return link_report

def check_technical_aspects(soup):
    """Проверка технических аспектов"""
    tech_report = {}
    
    # Проверка наличия viewport
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    tech_report['viewport'] = bool(viewport)
    
    # Проверка наличия языка HTML
    html_tag = soup.find('html')
    if html_tag:
        lang = html_tag.get('lang')
        tech_report['html_lang'] = lang if lang else 'Не указан'
    else:
        tech_report['html_lang'] = 'Не найден'
    
    # Проверка наличия favicon
    favicon = soup.find('link', attrs={'rel': 'icon'}) or soup.find('link', attrs={'rel': 'shortcut icon'})
    tech_report['favicon'] = bool(favicon)
    
    # Проверка наличия структурированных данных (ограниченно)
    structured_data = soup.find('script', attrs={'type': 'application/ld+json'})
    tech_report['structured_data'] = bool(structured_data)
    
    return tech_report

def main():
    url = "https://www.aerodrom-gelion.ru/"
    
    print("Начинаем полный анализ сайта aerodrom-gelion.ru...")
    
    try:
        # Получаем содержимое сайта
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Ошибка при получении сайта: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Анализ времени загрузки
        print("\n1. Анализ времени загрузки...")
        load_time, status = check_page_load_time(url)
        if load_time:
            print(f"   Время загрузки: {load_time:.2f} секунд")
            print(f"   Статус: {status}")
        else:
            print(f"   Ошибка при измерении времени загрузки: {status}")
        
        # SEO анализ
        print("\n2. SEO анализ...")
        seo_report = analyze_seo_elements(soup)
        print(f"   Заголовок: '{seo_report['title']['text']}' (длина: {seo_report['title']['length']} символов)")
        print(f"   Описание: '{seo_report['description']['content']}' (длина: {seo_report['description']['length']} символов)")
        print(f"   Ключевые слова: {seo_report['keywords']['content']}")
        print(f"   Заголовки H1: {seo_report['headings']['h1_count']} шт. - {seo_report['headings']['h1_text']}")
        print(f"   Заголовки H2: {seo_report['headings']['h2_count']} шт.")
        print(f"   Заголовки H3: {seo_report['headings']['h3_count']} шт.")
        
        # Анализ изображений
        print("\n3. Анализ изображений...")
        img_report = check_images_optimization(soup, url)
        print(f"   Всего изображений: {img_report['total']}")
        print(f"   Изображений без alt-атрибута: {img_report['missing_alt']}")
        print(f"   Оптимизированных изображений: {img_report['optimized']}")
        print(f"   Неоптимизированных изображений: {img_report['unoptimized']}")
        
        # Анализ ссылок
        print("\n4. Анализ ссылок...")
        link_report = check_links_status(soup, url)
        print(f"   Всего ссылок: {link_report['total']}")
        print(f"   Рабочих ссылок: {link_report['working']}")
        print(f"   Сломанных ссылок: {link_report['broken']}")
        print(f"   Внешних ссылок: {link_report['external']}")
        
        # Технический анализ
        print("\n5. Технический анализ...")
        tech_report = check_technical_aspects(soup)
        print(f"   Наличие viewport: {tech_report['viewport']}")
        print(f"   Язык HTML: {tech_report['html_lang']}")
        print(f"   Наличие favicon: {tech_report['favicon']}")
        print(f"   Наличие структурированных данных: {tech_report['structured_data']}")
        
        # Формирование общего отчета
        print("\n6. Общий отчет:")
        
        issues = []
        
        # SEO проблемы
        if seo_report['title']['length'] < 10 or seo_report['title']['length'] > 60:
            issues.append(f"Заголовок страницы не оптимален по длине (рекомендуется 10-60 символов): {seo_report['title']['length']}")
        
        if seo_report['description']['length'] < 50 or seo_report['description']['length'] > 160:
            issues.append(f"Мета-описание не оптималено по длине (рекомендуется 50-160 символов): {seo_report['description']['length']}")
        
        if seo_report['headings']['h1_count'] != 1:
            issues.append(f"Количество H1 заголовков не оптимально (рекомендуется 1): {seo_report['headings']['h1_count']}")
        
        # Технические проблемы
        if not tech_report['viewport']:
            issues.append("Отсутствует мета-тег viewport (важен для адаптивности)")
        
        if tech_report['html_lang'] == 'Не указан':
            issues.append("Не указан язык HTML (lang атрибут)")
        
        if img_report['missing_alt'] > 0:
            issues.append(f"Найдено {img_report['missing_alt']} изображений без alt-атрибута")
        
        if load_time and load_time > 3:
            issues.append(f"Время загрузки страницы слишком медленное: {load_time:.2f} секунд (рекомендуется < 3 секунды)")
        
        if issues:
            print("\n   Найденные проблемы:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n   Проблем не найдено!")
        
        # Рекомендации
        recommendations = []
        
        if load_time and load_time > 3:
            recommendations.append("Оптимизировать время загрузки страницы: сжать изображения, использовать кэширование, минимизировать CSS/JS")
        
        if tech_report['html_lang'] == 'Не указан':
            recommendations.append("Добавить атрибут lang к HTML тегу (например, <html lang='ru'>)")
        
        if not tech_report['viewport']:
            recommendations.append("Добавить мета-тег viewport для адаптивности: <meta name='viewport' content='width=device-width, initial-scale=1'>")
        
        if img_report['missing_alt'] > 0:
            recommendations.append("Добавить alt-атрибуты ко всем изображениям для улучшения SEO и доступности")
        
        if seo_report['headings']['h1_count'] != 1:
            recommendations.append("Убедиться, что на странице есть только один H1 заголовок, описывающий основную тему страницы")
        
        if recommendations:
            print("\n   Рекомендации по улучшению:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("\n   Рекомендаций по улучшению нет!")
        
        # Сохранение отчета в файл
        report_content = f"""# Отчет по анализу сайта aerodrom-gelion.ru

## Общая информация
- URL: {url}
- Статус: {response.status_code}
- Время загрузки: {load_time:.2f} секунд

## SEO Анализ
- Заголовок: '{seo_report['title']['text']}' ({seo_report['title']['length']} символов)
- Описание: '{seo_report['description']['content']}' ({seo_report['description']['length']} символов)
- Ключевые слова: {seo_report['keywords']['content']}
- Заголовки H1: {seo_report['headings']['h1_count']} шт. - {seo_report['headings']['h1_text']}
- Заголовки H2: {seo_report['headings']['h2_count']} шт.
- Заголовки H3: {seo_report['headings']['h3_count']} шт.

## Анализ изображений
- Всего изображений: {img_report['total']}
- Изображений без alt-атрибута: {img_report['missing_alt']}
- Оптимизированных изображений: {img_report['optimized']}
- Неоптимизированных изображений: {img_report['unoptimized']}

## Анализ ссылок
- Всего ссылок: {link_report['total']}
- Рабочих ссылок: {link_report['working']}
- Сломанных ссылок: {link_report['broken']}
- Внешних ссылок: {link_report['external']}

## Технический анализ
- Наличие viewport: {tech_report['viewport']}
- Язык HTML: {tech_report['html_lang']}
- Наличие favicon: {tech_report['favicon']}
- Наличие структурированных данных: {tech_report['structured_data']}

## Найденные проблемы
"""
        
        if issues:
            for i, issue in enumerate(issues, 1):
                report_content += f"{i}. {issue}\n"
        else:
            report_content += "Проблем не найдено!\n"
        
        report_content += "\n## Рекомендации по улучшению\n"
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_content += f"{i}. {rec}\n"
        else:
            report_content += "Рекомендаций по улучшению нет!\n"
        
        # Записываем отчет в файл
        with open('AI_Agency/Projects/Gelion Info/ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n   Отчет сохранен в файл: AI_Agency/Projects/Gelion Info/ANALYSIS_REPORT.md")
        
    except Exception as e:
        print(f"Произошла ошибка при анализе сайта: {str(e)}")

if __name__ == "__main__":
    main()