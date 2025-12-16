import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

BG_COLOR = "#F8F7FC"
PRIMARY = "#6D28D9"
ACCENT = "#E9D8FD"
TEXT = "#1F1B2E"

def notify(msg):
    messagebox.showinfo("Notification", msg)

class AppError(Exception):
    """Custom exception for application errors."""
    pass

# ---- Base page/class (Frame) ----
class AppPage(ttk.Frame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app        # reference to App instance (controller)
        self.db = app.db      # convenience alias


# ---- Login Page ----
class LoginPage(AppPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.build()


    def build(self):
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill="both", expand=True)
        container = tk.Frame(outer, bg=BG_COLOR)
        container.pack(expand=True)

        tk.Label(container, text="Login", font=("Arial", 22, "bold"),
                 bg=BG_COLOR, fg=PRIMARY).pack(pady=8)

        tk.Label(container, text="Email", bg=BG_COLOR).pack()
        self.login_email_entry = tk.Entry(container, width=40)
        self.login_email_entry.pack(pady=3)

        tk.Label(container, text="Password", bg=BG_COLOR).pack()
        self.login_password_entry = tk.Entry(container, width=40, show="*")
        self.login_password_entry.pack(pady=3)

        tk.Label(container, text="Role", bg=BG_COLOR).pack()
        self.login_role_var = tk.StringVar()
        ttk.Combobox(container, width=37, state="readonly",
                     textvariable=self.login_role_var,
                     values=["Client", "Freelancer", "Admin"]).pack(pady=5)

        tk.Button(container, text="Login", bg=PRIMARY, fg="white",
                  width=20, command=self.handle_login).pack(pady=12)

    def handle_login(self):
        try:
            role = self.login_role_var.get()
            email = self.login_email_entry.get().strip()
            pwd = self.login_password_entry.get().strip()

            if not email or not pwd or not role:
                raise AppError("All login fields are required.")

            if role == "Admin":
                # admin hardcoded
                if email == "admin@gmail.com" and pwd == "admin123":
                    notify("Admin Logged In")
                    self.app.current_user_email = email
                    self.app.current_role = role
                    self.app.open_role_dashboard("Admin")
                    self.app.admin_page.load_view()   # refresh admin view
                else:
                    raise AppError("Incorrect admin credentials.")
            else:
                try:
                    row = self.db.validate_login(email, pwd, role)
                except Exception as dbex:
                    raise AppError(f"DB error during login: {dbex}")

                if row:
                    notify(f"Logged in as {role}")
                    self.app.current_user_email = email
                    self.app.current_role = role
                    self.app.open_role_dashboard(role)
                    self.app.client_page.refresh_job_tables()
                    self.app.freelancer_page.refresh_jobs()
                else:
                    raise AppError("No such user. Please register first.")
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

# ---- Register Page ----
class RegisterPage(AppPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.build()

    def build(self):
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill="both", expand=True)
        container = tk.Frame(outer, bg=BG_COLOR)
        container.pack(expand=True)

        tk.Label(container, text="Register", font=("Arial", 22, "bold"),
                 bg=BG_COLOR, fg=PRIMARY).pack(pady=8)

        tk.Label(container, text="Full Name", bg=BG_COLOR).pack()
        self.reg_name_entry = tk.Entry(container, width=40)
        self.reg_name_entry.pack(pady=3)

        tk.Label(container, text="Email", bg=BG_COLOR).pack()
        self.reg_email_entry = tk.Entry(container, width=40)
        self.reg_email_entry.pack(pady=3)

        tk.Label(container, text="Password", bg=BG_COLOR).pack()
        self.reg_password_entry = tk.Entry(container, width=40, show="*")
        self.reg_password_entry.pack(pady=3)

        tk.Label(container, text="Role", bg=BG_COLOR).pack()
        self.reg_role_var = tk.StringVar()
        ttk.Combobox(container, width=37, state="readonly",
                     textvariable=self.reg_role_var,
                     values=["Client", "Freelancer"]).pack(pady=5)

        tk.Button(container, text="Register", bg=PRIMARY, fg="white",
                  width=20, command=self.register_user).pack(pady=12)

    def register_user(self):
        fullname = self.reg_name_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        role = self.reg_role_var.get().strip()


        if not fullname or not email or not password or not role:
                self.app.handle_error("All fields are required!")
                return
        
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Invalid email format")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        if role not in ("Client", "Freelancer"):
            messagebox.showerror("Error", "Please select a role")
            return

        # Database insert
        try:
            self.db.register_user(fullname, email, password, role)
            messagebox.showinfo("Success", "Registration successful!")

            self.reg_name_entry.delete(0, tk.END)
            self.reg_email_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_role_var.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {e}")

# ---- Client Dashboard ----
class ClientDashboard(AppPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.build()

    def build(self):
        outer = tk.Frame(self, bg=BG_COLOR, padx=15, pady=15)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Client Dashboard", font=("Arial", 20, "bold"),
                 bg=BG_COLOR, fg=PRIMARY).pack(pady=5)

        post = tk.LabelFrame(outer, text="Post Job", padx=10, pady=10, bg=BG_COLOR)
        post.pack(fill="x")

        tk.Label(post, text="Title:", bg=BG_COLOR).grid(row=0, column=0, sticky="w")
        self.client_title_entry = tk.Entry(post, width=40)
        self.client_title_entry.grid(row=0, column=1)

        tk.Label(post, text="Description:", bg=BG_COLOR).grid(row=1, column=0, sticky="nw")
        self.client_desc_entry = tk.Text(post, width=40, height=5)
        self.client_desc_entry.grid(row=1, column=1)

        tk.Label(post, text="Budget($):", bg=BG_COLOR).grid(row=2, column=0, sticky="w")
        self.client_budget_entry = tk.Entry(post, width=40)
        self.client_budget_entry.grid(row=2, column=1)

        tk.Label(post, text="Category:", bg=BG_COLOR).grid(row=3, column=0, sticky="w")
        self.client_category_var = tk.StringVar()
        ttk.Combobox(post, width=38, textvariable=self.client_category_var,
                     state="readonly",
                     values=["Technical", "Writing", "Design", "Business", "Other"]
        ).grid(row=3, column=1)
        self.client_category_var.set("Technical")

        tk.Button(post, text="Post Job", bg=PRIMARY, fg="white",
                  command=self.add_job).grid(row=4, column=1, sticky="e", pady=6)

        jobs_frame = tk.LabelFrame(outer, text="Your Jobs", bg=BG_COLOR)
        jobs_frame.pack(fill="both", expand=True, pady=10)

        self.client_job_table = ttk.Treeview(
            jobs_frame, columns=("ID", "Title", "Budget", "Category"), show="headings"
        )
        for col in ("ID", "Title", "Budget", "Category"):
            self.client_job_table.heading(col, text=col)
        self.client_job_table.pack(fill="both", expand=True)

        btn_row = tk.Frame(outer, bg=BG_COLOR)
        btn_row.pack(fill="x", pady=5)

        tk.Button(btn_row, text="Delete Selected Job", bg="red", fg="white",
                  command=self.client_delete_job).pack(side="left", padx=5)

        tk.Button(btn_row, text="View Applicants", bg=PRIMARY, fg="white",
                  command=self.client_view_applicants).pack(side="left", padx=5)

    def add_job(self):
        try:
            if self.app.current_role != "Client" or not self.app.current_user_email:
                raise AppError("You must be logged in as a Client to post jobs.")

            title = self.client_title_entry.get().strip()
            desc = self.client_desc_entry.get("1.0", "end").strip()
            budget = self.client_budget_entry.get().strip()

            if not title or not desc or not budget:
                raise AppError("All fields must be filled to post a job.")
            if not budget.isdigit():
                raise AppError("Budget must be a numeric value.")

            category = self.client_category_var.get()
            try:
                self.db.insert_job(title, desc, int(budget), category, self.app.current_user_email)
            except Exception as ex:
                raise AppError(f"DB error inserting job: {ex}")

            self.refresh_job_tables()
            notify("Job posted successfully!")
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

    def refresh_job_tables(self):
        # refresh client and freelancer views in App
        for r in self.client_job_table.get_children():
            self.client_job_table.delete(r)
        try:
            rows = self.db.get_jobs()
            for r in rows:
                jid = r[0]; title = r[1]; desc = r[2]; budget = r[3]; category = r[4]; client_email = r[5]
                if self.app.current_role == "Client" and self.app.current_user_email == client_email:
                    self.client_job_table.insert("", "end", values=(jid, title, budget, category))
        except Exception as ex:
            self.app.handle_error(f"DB error refreshing job tables: {ex}")

    def client_delete_job(self):
        try:
            sel = self.client_job_table.selection()
            if not sel:
                raise AppError("Select a job first.")
            jid = int(self.client_job_table.item(sel[0], "values")[0])
            try:
                self.db.delete_job(jid)
            except Exception as ex:
                raise AppError(f"DB error deleting job: {ex}")

            # remove Applications (DB.delete_job)
            try:
                self.db.cursor.execute("DELETE FROM Applications WHERE job_id=?", (jid,))
                self.db.conn.commit()
            except Exception:
                pass

            self.refresh_job_tables()
            self.app.freelancer_page.refresh_jobs()
            notify("Job deleted successfully!")
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

    def client_view_applicants(self):
        try:
            sel = self.client_job_table.selection()
            if not sel:
                raise AppError("Select a job first")

            jid = int(self.client_job_table.item(sel[0], "values")[0])

            apps = self.db.get_applications(jid)

            win = tk.Toplevel(self)
            win.title(f"Applicants for Job ID {jid}")
            win.geometry("600x400")

            tk.Label(
                win,
                text=f"Applicants for Job {jid}",
                font=("Arial", 14, "bold")
            ).pack(pady=10)

            if not apps:
                tk.Label(win, text="No applications yet.").pack()
                return

            frame = tk.Frame(win)
            frame.pack(fill="both", expand=True)

            tree = ttk.Treeview(
                frame,
                columns=("Name", "Email", "Skills"),
                show="headings"
            )

            tree.heading("Name", text="Name")
            tree.heading("Email", text="Email")
            tree.heading("Skills", text="Skills")

            tree.pack(fill="both", expand=True)

            for email, name, skills in apps:
                tree.insert("", "end", values=(name, email, skills))

        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")


# ---- Freelancer Dashboard ----
class FreelancerDashboard(AppPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.build()

    def build(self):
        outer = tk.Frame(self, bg=BG_COLOR, padx=12, pady=12)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Freelancer Dashboard",
                 font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=5)

        # search row
        search_row = tk.Frame(outer, bg=BG_COLOR)
        search_row.pack(fill="x")

        tk.Label(search_row, text="Search:", bg=BG_COLOR).pack(side="left")
        self.search_entry = tk.Entry(search_row, width=30)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(search_row, text="Go", bg=PRIMARY,fg="white",
                  command=self.search_jobs).pack(side="left")

        tk.Label(search_row, text="Category:", bg=BG_COLOR).pack(side="left", padx=12)
        self.filter_var = tk.StringVar()
        ttk.Combobox(
            search_row, width=15, state="readonly",
            textvariable=self.filter_var,
            values=["All", "Technical", "Writing", "Design", "Business", "Other"]
        ).pack(side="left")
        self.filter_var.set("All")

        tk.Button(search_row, text="Apply", bg=PRIMARY, fg="white",
                  command=self.search_jobs ).pack(side="left", padx=6)

        job_frame = tk.LabelFrame(outer, text="Available Jobs", bg=BG_COLOR)
        job_frame.pack(fill="both", expand=True)

        self.freelancer_job_table = ttk.Treeview(
            job_frame,
            columns=("ID", "Title", "Description", "Budget", "Category"),
            show="headings"
        )
        for col in ("ID", "Title", "Description", "Budget", "Category"):
            self.freelancer_job_table.heading(col, text=col)

        self.freelancer_job_table.column("ID", width=40, anchor="center")
        self.freelancer_job_table.column("Title", width=160)
        self.freelancer_job_table.column("Description", width=300)
        self.freelancer_job_table.column("Budget", width=70, anchor="center")
        self.freelancer_job_table.column("Category", width=100)

        self.freelancer_job_table.pack(fill="both", expand=True)

        tk.Button(outer, text="Apply for Selected Job", bg=PRIMARY, fg="white",
                  command=self.apply_selected_job).pack(pady=10)

        tk.Button(outer, text="Show All", command=self.refresh_jobs).pack()

        # initial load
        self.refresh_jobs()

    def refresh_jobs(self):
        for r in self.freelancer_job_table.get_children():
            self.freelancer_job_table.delete(r)
        try:
            rows = self.db.get_jobs()
            for r in rows:
                jid = r[0]; title = r[1]; desc = r[2]; budget = r[3]; category = r[4]; client_email = r[5]
                self.freelancer_job_table.insert("", "end", values=(jid, title, desc, budget, category))
        except Exception as ex:
            self.app.handle_error(f"DB error refreshing freelancer table: {ex}")

    def search_jobs(self):
        keyword = self.search_entry.get().lower()
        cat_filter = self.filter_var.get()
        for r in self.freelancer_job_table.get_children():
            self.freelancer_job_table.delete(r)
        try:
            rows = self.db.get_jobs()
            for r in rows:
                jid = r[0]; title = r[1]; desc = r[2]; budget = r[3]; category = r[4]; client_email = r[5]
                if keyword and keyword not in title.lower() and keyword not in desc.lower():
                    continue
                if cat_filter != "All" and category != cat_filter:
                    continue
                self.freelancer_job_table.insert("", "end", values=(jid, title, desc, budget, category))
        except Exception as ex:
            self.app.handle_error(f"DB error searching jobs: {ex}")

    def apply_selected_job(self):
        try:
            sel = self.freelancer_job_table.selection()
            if not sel:
                raise AppError("Select a job first.")
            jid = int(self.freelancer_job_table.item(sel[0], "values")[0])

            popup = tk.Toplevel(self)
            popup.title("Apply for Job")
            popup.geometry("350x250")
            popup.resizable(False, False)

            tk.Label(popup, text="Apply for Job", font=("Arial", 14, "bold")).pack(pady=10)

            tk.Label(popup, text="Your Name:").pack()
            name_entry = tk.Entry(popup, width=30); name_entry.pack(pady=5)
            tk.Label(popup, text="Your Skills:").pack()
            skills_entry = tk.Entry(popup, width=30); skills_entry.pack(pady=5)

            def submit_application():
                name = name_entry.get().strip()
                skills = skills_entry.get().strip()
                if not name:
                    messagebox.showerror("Error", "Name is required."); return
                if not skills:
                    messagebox.showerror("Error", "Skills are required."); return

                freelancer_email = self.app.current_user_email
                try:
                    self.db.insert_application(jid, freelancer_email, name, skills)
                except Exception as ex:
                    messagebox.showerror("DB Error", f"Error inserting application:\n{ex}")
                    return

                notify("Application submitted!")
                popup.destroy()

            tk.Button(popup, text="Submit", bg=PRIMARY, fg="white",
                      width=15, command=submit_application).pack(pady=15)
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

# ---- Admin Dashboard ----
class AdminDashboard(AppPage):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.build()

    def build(self):
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill="both", expand=True)

        menu = tk.Frame(outer, width=200, bg="#E4E7EC")
        menu.pack(side="left", fill="y")

        tk.Label(menu, text="Admin Menu", bg="#E4E7EC",fg= PRIMARY,
                 font=("Arial", 17, "bold")).pack(pady=10)

        tk.Button(menu, text="View Users", width=20,
                  command=self.show_users).pack(pady=5)

        tk.Button(menu, text="View Jobs", width=20,
                  command=self.show_jobs).pack(pady=5)

        tk.Button(menu, text="View Applications", width=20,
                  command=self.show_applications).pack(pady=5)

        self.admin_content = tk.Frame(outer, bg=BG_COLOR)
        self.admin_content.pack(side="right", fill="both", expand=True)

        self.show_jobs()   # default view

    # helpers
    def clear(self):
        for widget in self.admin_content.winfo_children():
            widget.destroy()

    def load_view(self):
        """Convenience for external refresh calls (e.g. after login)."""
        # if currently showing users/jobs/applications, refresh appropriately
        # We'll just call show_jobs to keep view consistent
        self.show_jobs()

    # Users view
    def show_users(self):
        self.clear()
        tk.Label(self.admin_content, text="User List", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=10)

        frame = tk.Frame(self.admin_content); frame.pack(fill="both", expand=True)
        self.admin_user_table = ttk.Treeview(frame, columns=("ID", "FullName", "Email", "Role"), show="headings")
        for col in ("ID", "FullName", "Email", "Role"):
            self.admin_user_table.heading(col, text=col)
        self.admin_user_table.pack(fill="both", expand=True)

        try:
            rows = self.db.get_all_users()
            for row in rows:
                clean_row = (row[0], str(row[1]).strip(), str(row[2]).strip(), str(row[3]).strip())
                self.admin_user_table.insert("", "end", values=clean_row)
        except Exception as ex:
            self.app.handle_error(f"DB error reading users: {ex}")

        btn_frame = tk.Frame(self.admin_content)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Delete Selected User", bg="red", fg="white",
                  command=self.admin_delete_user).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Edit Selected User", bg=PRIMARY, fg="white",
                  command=self.admin_edit_user).pack(side="left", padx=6)

    def admin_delete_user(self):
        try:
            sel = self.admin_user_table.selection()
            if not sel:
                raise AppError("Select a user first.")
            user_id = int(self.admin_user_table.item(sel[0], "values")[0])

            try:
                deleted = None
                # Prefer DB method
                if hasattr(self.db, "delete_user"): # hasattr returns whether the object has an attribute of the given name
                    # Some DB.delete_user implementations return boolean; others don't.
                    deleted = self.db.delete_user(user_id)
                else:
                    # fallback: run SQL
                    self.db.cursor.execute("DELETE FROM Users WHERE id=?", (user_id,))
                    self.db.conn.commit()
                    deleted = True

                # If DB.delete_user returned None treat as success (commit happened)
                if deleted is False:
                    raise AppError("User could not be deleted (not found).")

            except Exception as ex:
                raise AppError(f"DB error deleting user: {ex}")

            # refresh user list immediately
            self.show_users()
            notify("User deleted successfully!")
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

    # Edit user (pre-fill password, validate fields)
    def admin_edit_user(self):
        try:
            sel = self.admin_user_table.selection()
            if not sel:
                raise AppError("Select a user first.")
            values = self.admin_user_table.item(sel[0], "values")
            user_id, fullname, email, role = values
            user_id = int(user_id)

            # get full user record
            user = None
            if hasattr(self.db, "get_user_by_id"):
                user = self.db.get_user_by_id(user_id)
            else:
                # fallback: select from DB directly
                try:
                    self.db.cursor.execute("SELECT id, fullname, email, password, role FROM Users WHERE id=?", (user_id,))
                    user = self.db.cursor.fetchone()
                except Exception as ex:
                    raise AppError(f"DB error reading user: {ex}")

            if not user:
                raise AppError("User not found in database!")

            current_password = user[3]  # index 3 is password in expected tuple

            # Edit window
            win = tk.Toplevel(self)
            win.title("Edit User Details")
            win.geometry("380x320")
            win.transient(self)# make it a child of the main window
            win.grab_set()     # make it modal (user must interact with this first)
            win.lift()         # bring to front
            win.focus_force()  # force focus

            tk.Label(win, text="Full Name").pack(pady=(8,0))
            name_entry = tk.Entry(win); name_entry.pack(); name_entry.insert(0, fullname)

            tk.Label(win, text="Email").pack(pady=(8,0))
            email_entry = tk.Entry(win); email_entry.pack(); email_entry.insert(0, email)

            tk.Label(win, text="Password").pack(pady=(8,0))
            pass_entry = tk.Entry(win, show="*"); pass_entry.pack(); pass_entry.insert(0, current_password)

            tk.Label(win, text="Role").pack(pady=(8,0))
            role_var = tk.StringVar(value=role)
            tk.OptionMenu(win, role_var, "Client", "Freelancer").pack()

            def update_now():
                new_name = name_entry.get().strip()
                new_email = email_entry.get().strip()
                new_pass = pass_entry.get().strip()
                new_role = role_var.get().strip()

                # -----------------------
                # Validation (same as register)
                # -----------------------

                if not new_name or not new_email or not new_pass or not role:
                    messagebox.showerror("Error", "All fields are required!")
                    return

                if "@" not in new_email or "." not in new_email:
                    messagebox.showerror("Error", "Invalid email format")
                    return

                if len(new_pass) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters")
                    return

                if new_role not in ("Client", "Freelancer"):
                    messagebox.showerror("Error", "Invalid role selected")
                    return

                # -----------------------
                # Update DB
                # -----------------------
                try:
                    self.db.update_user(user_id, new_name, new_email, new_pass, new_role)

                    messagebox.showinfo("Success", "User updated successfully!")
                    win.destroy()
                    self.show_users()

                except Exception as ex:
                    self.app.handle_error(f"Update failed: {ex}")

                except AppError as e:
                        self.app.handle_error(str(e))
                            # except Exception as ex:
                            #     self.app.handle_error(f"Unexpected error: {ex}")

            tk.Button(win, text="Save", bg="green", fg="white", command=update_now).pack(pady=10)
            tk.Button(win, text="Cancel", bg="gray", fg="white", command=win.destroy).pack()
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

    # Jobs view
    def show_jobs(self):
        
        self.clear()

        tk.Label(self.admin_content, text="All Jobs", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=10)

        frame = tk.Frame(self.admin_content); frame.pack(fill="both", expand=True)
        self.admin_job_table = ttk.Treeview(frame, columns=("ID", "Title", "Budget", "Category", "ClientEmail"), show="headings")
        for c in ("ID", "Title", "Budget", "Category", "ClientEmail"):

            self.admin_job_table.heading(c, text=c)
        self.admin_job_table.pack(fill="both", expand=True)

        try:
            rows = self.db.get_jobs()
            for r in rows:
                jid = r[0]; title = r[1]; desc = r[2]; budget = r[3]; category = r[4]; client_email = r[5]
                self.admin_job_table.insert("", "end", values=(jid, title, budget, category, client_email))
        except Exception as ex:
            self.app.handle_error(f"DB error fetching jobs: {ex}")

        tk.Button(self.admin_content, text="Delete Selected Job", bg="red", fg="white", command=self.admin_delete_job).pack(pady=10)

    def admin_delete_job(self):
        try:
            row = self.admin_job_table.selection()[0]
            job_id = int(self.admin_job_table.item(row, "values")[0])
            try:
                self.db.delete_job(job_id)
            except Exception as ex:
                raise AppError(f"DB error deleting job: {ex}")
            # refresh
            self.show_jobs()
            self.app.client_page.refresh_job_tables()
            self.app.freelancer_page.refresh_jobs()
            notify("Deleted successfully")
        except IndexError:
            self.app.handle_error("Select a job first")
        except AppError as e:
            self.app.handle_error(str(e))
        except Exception as ex:
            self.app.handle_error(f"Unexpected error: {ex}")

    # Applications view
    def show_applications(self):
        self.clear()
        tk.Label(self.admin_content, text="Applications", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=10)

        frame = tk.Frame(self.admin_content); frame.pack(fill="both", expand=True)
        self.admin_app_table = ttk.Treeview(frame, columns=("JobID", "JobTitle", "Email", "Name", "Skills"), show="headings")
        self.admin_app_table.heading("JobID", text="Job ID")
        self.admin_app_table.heading("JobTitle", text="Job Title")
        self.admin_app_table.heading("Email", text="Freelancer Email")
        self.admin_app_table.heading("Name", text="Name")
        self.admin_app_table.heading("Skills", text="Skills")

        self.admin_app_table.column("JobID", width=60, anchor="center")
        self.admin_app_table.column("JobTitle", width=180)
        self.admin_app_table.column("Email", width=200)
        self.admin_app_table.column("Name", width=160)
        self.admin_app_table.column("Skills", width=220)
        self.admin_app_table.pack(fill="both", expand=True)

        try:
            rows = self.db.get_all_applications()
            if not rows:
                messagebox.showinfo("Info", "No applications yet.")
                return

            for job_id, email, name, skills in rows:
                job_title = self.db.get_job_title(job_id) or "(Deleted Job)"
                self.admin_app_table.insert("", "end", values=(job_id, job_title, email, name, skills))
        except Exception as ex:
            self.app.handle_error(f"DB error fetching applications: {ex}")

# ---- Main App (controller) ----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freelancer Job Matching System")
        self.geometry("1000x680")
        self.configure(bg=BG_COLOR)

        # Database init with error handling
        try:
            self.db = Database()
        except Exception as ex:
            messagebox.showerror("DB Error", f"Failed to connect to DB: {ex}")
            raise

        self.current_user_email = None
        self.current_role = None

        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(expand=True, fill="both")

        # instantiate pages
        self.login_page = LoginPage(self.tabControl, self)
        self.register_page = RegisterPage(self.tabControl, self)
        self.client_page = ClientDashboard(self.tabControl, self)
        self.freelancer_page = FreelancerDashboard(self.tabControl, self)
        self.admin_page = AdminDashboard(self.tabControl, self)

        # add login & register initially
        self.tabControl.add(self.login_page, text="Login")
        self.tabControl.add(self.register_page, text="Register")
        # other pages will be added on demand

        self.tabControl.select(self.login_page)


    # central error handler
    def handle_error(self, message):
        messagebox.showerror("Error", message)

    def add_tab_if_missing(self, frame, title):
        if str(frame) not in self.tabControl.tabs():
            self.tabControl.add(frame, text=title)

    def remove_tab_if_present(self, frame):
        if str(frame) in self.tabControl.tabs():
            self.tabControl.forget(frame)

    def open_role_dashboard(self, role):
        if role == "Client":
            self.add_tab_if_missing(self.client_page, "Client Dashboard")
            self.tabControl.select(self.client_page)
        elif role == "Freelancer":
            self.add_tab_if_missing(self.freelancer_page, "Freelancer Dashboard")
            self.tabControl.select(self.freelancer_page)
        elif role == "Admin":
            self.add_tab_if_missing(self.admin_page, "Admin Panel")
            self.tabControl.select(self.admin_page)

if __name__ == "__main__":
    App().mainloop()
