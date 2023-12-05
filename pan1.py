from panzoom import PanZoom
import flet as ft


def main(page: ft.Page):
    img = ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER)

    row = ft.Row()
    col1 = ft.Column(width=400,
                     controls=[ft.Text('Begin1')])
    # both dimensions smaller than the image but ratio is the same
    col1.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=100, height=100,
                                 padding_color='pink'))
    # both dimensions smaller than the image but viewport is wider in ratio
    col1.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=150, height=100,
                                 padding_color='pink'))
    # both dimensions smaller than the image but viewport is taller in ratio
    col1.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=100, height=150,
                                 padding_color='pink'))
    # width is larger than the image but height is smaller
    col1.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=250, height=100,
                                 padding_color='pink'))

    # height is larger than the image but width is smaller
    col1.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=100, height=250,
                                 padding_color='pink'))

    col1.controls.append(ft.Text('End1'))
    col2 = ft.Column(width=400,
                     controls=[ft.Text('Begin2')])

    # both width and height is larger than the content
    col2.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=250, height=250,
                                 padding_color='pink'))

    # both width and height is larger than the content but wider
    col2.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=300, height=250,
                                 padding_color='pink'))

    # both width and height is larger than the content but taller
    col2.controls.append(PanZoom(ft.Image(src='/img/Square_200x200.png', fit=ft.ImageFit.COVER),
                                 200, 200,
                                 width=250, height=300,
                                 padding_color='pink'))
    col2.controls.append(ft.Text('End2'))
    row.controls.append(col1)
    row.controls.append(col2)
    page.add(ft.Container(width=800, height=1000, content=row, padding=5, bgcolor='lightblue'))


ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8080)

