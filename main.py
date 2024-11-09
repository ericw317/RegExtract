import flet as ft
import os
import shutil
from CustomLibs import ShadowCopies

# get users
def get_users():
    user_exclusion = ["Default", "Default User", "Public", "All Users"]  # exclusion list
    users_path = "C:\\Users"  # set path to users folder
    user_list = []

    # populate user list
    for user in os.listdir(users_path):
        if os.path.isdir(os.path.join(users_path, user)) and user not in user_exclusion:
            user_list.append(user)

    return user_list

# copy locked registry files
def copy_reg(reg_file, destination_path, user=None):
    # set path
    if user is None:
        reg_path = f"Windows\\System32\\config\\{reg_file}"
    else:
        reg_path = f"Users\\{user}\\NTUSER.DAT"

    # create shadow copy
    ShadowCopies.create_shadow_copy()
    shadow_copy_path = ShadowCopies.get_latest_shadow_copy()
    reg_source = os.path.join(shadow_copy_path, reg_path)

    # copy reg file from shadow copy
    shutil.copy(reg_source, os.path.join(destination_path, f"{reg_file}_copy"))

    # delete shadow copy
    shadow_ID = ShadowCopies.get_latest_shadow_copy_id()
    ShadowCopies.delete_shadow_copy(shadow_ID)


def main(page: ft.Page):
    # page settings
    page.title = "RegExtract"

    # variables
    user_list = get_users()

    # button and dropdown functions
    def dropdown_change(e):
        if dd_reg_file.value == "NTUSER.DAT":
            dd_user.disabled = False
            page.update()
        else:
            dd_user.disabled = True
            dd_user.value = None
            page.update()

    def get_output_dir(e: ft.FilePickerResultEvent):
        if e.path:
            t_output_dir.value = e.path
            t_output_dir.update()
        else:
            "Cancelled"
        return 0

    # general functions
    def extract():
        if input_validation():
            # open loading screen and prevent user from closing page
            page.dialog = dlg_progress
            page.window_prevent_close = True
            dlg_progress.title = ft.Text(f"Extracting {dd_reg_file.value}")
            open_dlg_progress()
            page.update()

            # extract the registry file
            if dd_reg_file.value != "NTUSER.DAT":
                try:
                    copy_reg(dd_reg_file.value, t_output_dir.value)
                except Exception:
                    page.dialog = dlg_error
                    dlg_error.content = ft.Text("Error: Make sure you're running as administrator.")
                    dlg_error.open = True
                    page.update()
            elif dd_reg_file.value == "NTUSER.DAT":
                try:
                    copy_reg(dd_reg_file.value, t_output_dir.value, dd_user.value)
                except Exception:
                    page.dialog = dlg_error
                    dlg_error.content = ft.Text("Error: Make sure you're running as administrator.")
                    dlg_error.open = True
                    page.update()

            # close loading screen and re-allow user to close page
            page.window_prevent_close = False
            dlg_progress.open = False
            page.update()

    def input_validation():
        if dd_reg_file.value is None:
            page.dialog = dlg_error
            dlg_error.content = ft.Text("No registry file selected")
            dlg_error.open = True
            page.update()
            return False
        elif dd_user.value not in user_list and dd_reg_file.value == "NTUSER.DAT":
            page.dialog = dlg_error
            dlg_error.content = ft.Text("No user selected")
            dlg_error.open = True
            page.update()
            return False
        elif not os.path.exists(t_output_dir.value):
            page.dialog = dlg_error
            dlg_error.content = ft.Text("Invalid output directory")
            dlg_error.open = True
            page.update()
            return False
        return True

    # dialog functions
    def open_dlg_progress():
        page.dialog = dlg_progress
        dlg_progress.open = True
        page.update()

    # dropdowns
    dd_reg_file = ft.Dropdown(
        label="Registry File",
        options=[
            ft.dropdown.Option("SYSTEM"),
            ft.dropdown.Option("SOFTWARE"),
            ft.dropdown.Option("SAM"),
            ft.dropdown.Option("SECURITY"),
            ft.dropdown.Option("NTUSER.DAT")
        ],
        on_change=dropdown_change
    )
    dd_user = ft.Dropdown(
        label="User (if NTUSER.DAT is selected)",
        options=[],
        disabled=True
    )

    # populate user list
    for user in user_list:
        dd_user.options.append(ft.dropdown.Option(user))

    # text fields
    t_output_dir = ft.TextField(label="Output Directory", read_only=True)

    # buttons
    b_select_output = ft.ElevatedButton(
        text="Select Output Directory",
        height=50,
        on_click=lambda _: dlg_output_dir.get_directory_path()
    )
    b_extract = ft.ElevatedButton(
        text="Extract",
        height=50,
        on_click=lambda _: extract()
    )

    # dialogues
    dlg_output_dir = ft.FilePicker(on_result=get_output_dir)
    page.overlay.append(dlg_output_dir)
    dlg_error = ft.AlertDialog(title=ft.Text("Error"))
    dlg_progress = ft.AlertDialog(
        title=ft.Text("Extraction In Progress"),
        content=ft.ProgressRing(width=25, height=25, stroke_width=2),
        actions_alignment=ft.MainAxisAlignment.CENTER,
        modal=True
    )

    # page display
    page.add(
        ft.Column([
            ft.Row([
                ft.Text("RegExtract", size=40)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                dd_reg_file, dd_user
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                t_output_dir, b_select_output
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                b_extract
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True, alignment=ft.MainAxisAlignment.CENTER)
    )


ft.app(main)
