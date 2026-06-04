import flet as ft
import subprocess
import sys
import os

def main(page: ft.Page):
    page.title = "آزمون سنجش اعتماد کودکان"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 800
    page.window_height = 600

    title = ft.Text("آزمون سنجش اعتماد کودکان", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
    
    subtitle = ft.Text("لطفاً جنسیت خود را انتخاب کنید", size=20, color=ft.Colors.GREY_600)
    
    def start_girl(e):
        print("شروع تست دختران")
        try:
            original_file = os.path.join(os.path.dirname(__file__), "run.py")
            subprocess.Popen([sys.executable, original_file])
        except Exception as ex:
            print(f"خطا: {ex}")
    
    def start_boy(e):
        print("شروع تست پسران")
        try:
            original_file = os.path.join(os.path.dirname(__file__), "run.py")
            subprocess.Popen([sys.executable, original_file])
        except Exception as ex:
            print(f"خطا: {ex}")

    girl_button = ft.ElevatedButton(
        content=ft.Text("دختران", size=24, weight=ft.FontWeight.BOLD),
        on_click=start_girl,
        width=200,
        height=80,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PINK_400,
        )
    )
    
    boy_button = ft.ElevatedButton(
        content=ft.Text("پسران", size=24, weight=ft.FontWeight.BOLD),
        on_click=start_boy,
        width=200,
        height=80,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_400,
        )
    )

    page.add(
        ft.Column(
            [
                title,
                ft.Container(height=30),
                subtitle,
                ft.Container(height=50),
                ft.Row([girl_button, boy_button], alignment=ft.MainAxisAlignment.CENTER, spacing=50),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)