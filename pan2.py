from panzoom import PanZoom
import flet as ft


def main(page: ft.Page):
    img = ft.Image(
        src='/img/WikiMedia_Whole_world_-_land_and_oceans.jpg',
        fit=ft.ImageFit.COVER
    )

    panzoom = PanZoom(img, 512, 256,
                      width=300,
                      height=300,
                      padding_color='red',  on_click=lambda e: print(f'CLICK {e.local_x} {e.local_y}'))
    col = ft.Column(width=1400,
                    controls=[ft.Text('Hello World1'),
                              panzoom,
                              ft.Text('Hello World2')])

    page.add(ft.Container(width=800, height=800, content=col, padding=5, bgcolor='lightblue'))


ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8080)
