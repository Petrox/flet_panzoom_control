from panzoom import PanZoom
import flet as ft


def main(page: ft.Page):
    content = ft.Column([
        ft.ElevatedButton(icon=ft.icons.NUMBERS, text='Hello World',
                          width=600, height=100,
                          on_click=lambda: print('Hello World')),
        ft.ElevatedButton(icon=ft.icons.NUMBERS, text='Hello World2',
                          width=600, height=100,
                          on_click=lambda: print('Hello World2'))])

    panzoom = PanZoom(content, 600, 200,
                      width=600,
                      height=150,
                      padding_color='red', on_click=lambda e: print(f'CLICK {e.local_x} {e.local_y}'))
    col = ft.Column(width=1400,
                    controls=[ft.Text('Hello World1'),
                              panzoom,
                              ft.Text('Hello World2')])

    page.add(ft.Container(width=800, height=800, content=col, padding=5, bgcolor='lightblue'))


ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8080)
