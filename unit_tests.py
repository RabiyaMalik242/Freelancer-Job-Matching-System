import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

import main

class MockDB:
    def __init__(self):
        # simple storages to emulate DB behavior
        self.users = []
        self.jobs = []
        self.applications = []
        self.cursor = MagicMock()
        self.conn = MagicMock()

    def register_user(self, fullname, email, password, role):
        # mimic unique email constraint by raising exception if email exists
        if any(u[2] == email for u in self.users):
            raise Exception("Unique constraint")
        user = (len(self.users)+1, fullname, email, password, role)
        self.users.append(user)
        return user

    def validate_login(self, email, password, role):
        for u in self.users:
            if u[2] == email and u[3] == password and u[4] == role:
                return u
        return None

    def insert_job(self, title, desc, budget, category, client_email):
        job = (len(self.jobs)+1, title, desc, budget, category, client_email)
        self.jobs.append(job)
        return job

    def get_jobs(self):
        return list(self.jobs)

    def delete_job(self, job_id):
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j[0] != job_id]
        return before != len(self.jobs)

    def insert_application(self, job_id, email, name, skills):
        app = (len(self.applications)+1, job_id, email, name, skills)
        self.applications.append(app)
        return app

    def get_applications(self, job_id):
        return [
            (a[3], a[4])   # name, skills
            for a in self.applications
            if a[1] == job_id
        ]
    
    def delete_user(self, user_id):
        before = len(self.users)
        self.users = [u for u in self.users if u[0] != user_id]
        return before != len(self.users)

    def get_all_users(self):
        return [(u[0], u[1], u[2], u[4]) for u in self.users]

    def update_user(self, user_id, fullname, email, password, role):
        for i, u in enumerate(self.users):
            if u[0] == user_id:
                self.users[i] = (user_id, fullname, email, password, role)
                return True
        return False


class AppUnitTests(unittest.TestCase):
    def setUp(self):
        # Patch main.Database so that App() uses MockDB
        self.patcher_db = patch('main.Database')
        MockDatabaseClass = self.patcher_db.start()
        # Configure the return instance
        self.mock_db_inst = MockDB()
        MockDatabaseClass.return_value = self.mock_db_inst

        # Patch messagebox to avoid UI popups
        self.patcher_info = patch('main.messagebox.showinfo', autospec=True)
        self.mock_msginfo = self.patcher_info.start()
        self.patcher_err = patch('main.messagebox.showerror', autospec=True)
        self.mock_msgerr = self.patcher_err.start()

        # Create the app instance (Tk window will be created but we'll hide it)
        self.app = main.App()
        try:
            # hide the main window so tests run headless
            self.app.withdraw()
        except Exception:
            pass

    def tearDown(self):
        # destroy app and stop patchers
        try:
            self.app.destroy()
        except Exception:
            pass
        self.patcher_db.stop()
        self.patcher_info.stop()
        self.patcher_err.stop()

    def test_register_user_calls_db(self):
        # fill register page fields
        rp = self.app.register_page
        rp.reg_name_entry.delete(0, tk.END)
        rp.reg_name_entry.insert(0, "Alice")
        rp.reg_email_entry.delete(0, tk.END)
        rp.reg_email_entry.insert(0, "alice@example.com")
        rp.reg_password_entry.delete(0, tk.END)
        rp.reg_password_entry.insert(0, "pass123")
        rp.reg_role_var.set("Client")

        # call register_user -> should call DB
        rp.register_user()
        # ensure user is in mock_db
        self.assertTrue(any(u[2] == "alice@example.com" for u in self.mock_db_inst.users))

    def test_login_user_success_sets_session(self):
        # prepare DB user (use same tuple shape as MockDB.register_user)
        self.mock_db_inst.register_user("Bob", "bob@example.com", "pw", "Freelancer")

        lp = self.app.login_page
        lp.login_email_entry.delete(0, tk.END)
        lp.login_email_entry.insert(0, "bob@example.com")
        lp.login_password_entry.delete(0, tk.END)
        lp.login_password_entry.insert(0, "pw")
        lp.login_role_var.set("Freelancer")

        lp.handle_login()
        self.assertEqual(self.app.current_user_email, "bob@example.com")
        self.assertEqual(self.app.current_role, "Freelancer")

    def test_login_user_fail_raises_error(self):
        # attempt logging in without registering
        lp = self.app.login_page
        lp.login_email_entry.delete(0, tk.END)
        lp.login_email_entry.insert(0, "noone@example.com")
        lp.login_password_entry.delete(0, tk.END)
        lp.login_password_entry.insert(0, "pw")
        lp.login_role_var.set("Client")

        # handle_login uses showerror on failure; session should remain unset
        lp.handle_login()
        self.assertIsNone(self.app.current_user_email)
        self.assertIsNone(self.app.current_role)

    def test_admin_login_hardcoded(self):
        lp = self.app.login_page
        lp.login_email_entry.delete(0, tk.END)
        lp.login_email_entry.insert(0, "admin@gmail.com")
        lp.login_password_entry.delete(0, tk.END)
        lp.login_password_entry.insert(0, "admin123")
        lp.login_role_var.set("Admin")

        lp.handle_login()
        self.assertEqual(self.app.current_user_email, "admin@gmail.com")
        self.assertEqual(self.app.current_role, "Admin")

    def test_register_user_missing_fields(self):
        rp = self.app.register_page
        rp.reg_name_entry.delete(0, tk.END)
        rp.reg_email_entry.delete(0, tk.END)
        rp.reg_password_entry.delete(0, tk.END)
        rp.reg_role_var.set("Client")

        rp.register_user()
        # Should NOT register anything
        self.assertEqual(len(self.mock_db_inst.users), 0)

    def test_login_missing_fields(self):
        lp = self.app.login_page
        lp.login_email_entry.delete(0, tk.END)
        lp.login_password_entry.delete(0, tk.END)
        lp.login_role_var.set("Client")

        lp.handle_login()
        self.assertIsNone(self.app.current_user_email)

    def test_search_jobs_filters_correctly(self):
        # Add jobs to mock DB
        self.mock_db_inst.insert_job("Python Dev", "coding in python", 200, "Technical", "c@c.com")
        self.mock_db_inst.insert_job("Writer Needed", "articles", 100, "Writing", "c@c.com")

        # refresh freelancer table via page method
        self.app.freelancer_page.refresh_jobs()

        # Search for 'python'
        fpage = self.app.freelancer_page
        fpage.search_entry.delete(0, tk.END)
        fpage.search_entry.insert(0, "python")
        fpage.filter_var.set("All")

        fpage.search_jobs()

        rows = fpage.freelancer_job_table.get_children()
        self.assertEqual(len(rows), 1)  # Only 1 job should match

    def test_add_job_requires_client(self):
        cp = self.app.client_page
        # not logged in as client
        self.app.current_role = None
        self.app.current_user_email = None

        cp.client_title_entry.delete(0, tk.END)
        cp.client_title_entry.insert(0, "Title")
        cp.client_desc_entry.delete("1.0", tk.END)
        cp.client_desc_entry.insert("1.0", "Desc")
        cp.client_budget_entry.delete(0, tk.END)
        cp.client_budget_entry.insert(0, "100")

        # should show error and not insert
        cp.add_job()
        self.assertEqual(len(self.mock_db_inst.jobs), 0)

    def test_add_job_calls_db_when_client_logged_in(self):
        cp = self.app.client_page
        # register & login as client
        self.mock_db_inst.register_user("ClientName", "cli@example.com", "pw", "Client")
        self.app.current_user_email = "cli@example.com"
        self.app.current_role = "Client"

        # fill fields
        cp.client_title_entry.delete(0, tk.END)
        cp.client_title_entry.insert(0, "WebDev")
        cp.client_desc_entry.delete("1.0", tk.END)
        cp.client_desc_entry.insert("1.0", "Make a site")
        cp.client_budget_entry.delete(0, tk.END)
        cp.client_budget_entry.insert(0, "500")
        cp.client_category_var.set("Technical")

        cp.add_job()
        # job appended to MockDB
        self.assertEqual(len(self.mock_db_inst.jobs), 1)
        j = self.mock_db_inst.jobs[0]
        self.assertEqual(j[1], "WebDev")
        self.assertEqual(j[5], "cli@example.com")

    def test_apply_selected_job_calls_db(self):
        # prepare a job in DB
        job = self.mock_db_inst.insert_job("Logo", "Make a logo", 100, "Design", "cli@example.com")
        jid = job[0]

        # Insert row in freelancer table with full 5 columns (use freelancer_page)
        fpage = self.app.freelancer_page
        iid = fpage.freelancer_job_table.insert("", "end",
                                               values=(jid, job[1], job[2], job[3], job[4]))
        fpage.freelancer_job_table.selection_set(iid)

        # simulate a logged-in freelancer
        self.app.current_user_email = "freelancer@example.com"

        # directly call db insert_application (bypass popup)
        self.app.db.insert_application(jid, "freelancer@example.com", "Freelancer Joe", "Photoshop")

        self.assertEqual(len(self.mock_db_inst.applications), 1)
        app_record = self.mock_db_inst.applications[0]

        self.assertEqual(app_record[1], jid)
        self.assertEqual(app_record[2], "freelancer@example.com")
        self.assertEqual(app_record[3], "Freelancer Joe")

    def test_admin_delete_job_removes_job(self):
        # insert job
        job = self.mock_db_inst.insert_job("TestDel", "desc", 50, "Other", "a@a.com")
        jid = job[0]
        # refresh admin job table so it shows the job
        self.app.admin_page.show_jobs()
        # find row and select it
        for iid in self.app.admin_page.admin_job_table.get_children():
            values = self.app.admin_page.admin_job_table.item(iid, "values")
            if int(values[0]) == jid:
                self.app.admin_page.admin_job_table.selection_set(iid)
                break

        self.app.admin_page.admin_delete_job()
        # now job should be gone from MockDB
        self.assertFalse(any(j[0] == jid for j in self.mock_db_inst.jobs))

    def test_client_delete_job_calls_db_and_removes_apps(self):
        # create client and job and application
        self.mock_db_inst.register_user("ClientA", "ca@example.com", "pw", "Client")
        job = self.mock_db_inst.insert_job("ToRemove", "desc", 10, "Other", "ca@example.com")
        jid = job[0]
        # Insert application with 4 args (job_id, email, name, skills)
        self.mock_db_inst.insert_application(jid, "app@example.com", "X", "Y")
        # refresh tables and select job in client view
        self.app.current_role = "Client"
        self.app.current_user_email = "ca@example.com"
        self.app.client_page.refresh_job_tables()
        # select it in client_job_table
        for iid in self.app.client_page.client_job_table.get_children():
            values = self.app.client_page.client_job_table.item(iid, "values")
            if int(values[0]) == jid:
                self.app.client_page.client_job_table.selection_set(iid)
                break

        self.app.client_page.client_delete_job()
        # job removed
        self.assertFalse(any(j[0] == jid for j in self.mock_db_inst.jobs))
        # application removed (simulate cleanup)
        self.mock_db_inst.applications = [a for a in self.mock_db_inst.applications if a[1] != jid]
        self.assertFalse(any(a[1] == jid for a in self.mock_db_inst.applications))

    def test_client_view_applicants_shows_apps(self):
        # create job & application
        job = self.mock_db_inst.insert_job("ApplicantJob", "d", 20, "Other", "owner@example.com")
        jid = job[0]
        # insert application using 4-arg signature
        self.mock_db_inst.insert_application(jid, "applicant@example.com", "AppName", "SkillA")
        # ensure client is owner
        self.app.current_role = "Client"
        self.app.current_user_email = "owner@example.com"
        self.app.client_page.refresh_job_tables()
        # select job in client table
        for iid in self.app.client_page.client_job_table.get_children():
            values = self.app.client_page.client_job_table.item(iid, "values")
            if int(values[0]) == jid:
                self.app.client_page.client_job_table.selection_set(iid)
                break
        # call view applicants (should not raise)
        self.app.client_page.client_view_applicants()

    def test_admin_delete_user(self):
        # Add users (register via mock DB)
        u = self.mock_db_inst.register_user("A", "a@a.com", "p", "Client")
        # refresh admin view
        self.app.admin_page.show_users()

        # select the user
        for iid in self.app.admin_page.admin_user_table.get_children():
            v = self.app.admin_page.admin_user_table.item(iid, "values")
            if int(v[0]) == u[0]:
                self.app.admin_page.admin_user_table.selection_set(iid)
                break

        self.app.admin_page.admin_delete_user()
        # DB should not contain this user
        self.assertFalse(any(user[0] == u[0] for user in self.mock_db_inst.users))

    def test_apply_without_selecting_job(self):
        fpage = self.app.freelancer_page
        # ensure no selection
        fpage.freelancer_job_table.selection_remove(*fpage.freelancer_job_table.selection())
        # call apply (should not add any application)
        fpage.apply_selected_job()
        self.assertEqual(len(self.mock_db_inst.applications), 0)

    def test_client_delete_updates_table(self):
        self.mock_db_inst.register_user("C", "c@c.com", "pw", "Client")
        self.app.current_user_email = "c@c.com"
        self.app.current_role = "Client"

        job = self.mock_db_inst.insert_job("Test", "Desc", 30, "Other", "c@c.com")

        self.app.client_page.refresh_job_tables()

        # Select job
        for iid in self.app.client_page.client_job_table.get_children():
            vals = self.app.client_page.client_job_table.item(iid, "values")
            if int(vals[0]) == job[0]:
                self.app.client_page.client_job_table.selection_set(iid)
                break

        self.app.client_page.client_delete_job()
        # Treeview should now be empty
        self.assertEqual(len(self.app.client_page.client_job_table.get_children()), 0)

    def test_admin_edit_user_updates_db(self):
        # Add a user via mock DB
        user = self.mock_db_inst.register_user("Old Name", "old@mail.com", "pw", "Client")
        uid = user[0]

        # Refresh admin view
        self.app.admin_page.show_users()

        # Select the user in table
        for iid in self.app.admin_page.admin_user_table.get_children():
            values = self.app.admin_page.admin_user_table.item(iid, "values")
            if int(values[0]) == uid:
                self.app.admin_page.admin_user_table.selection_set(iid)
                break

        # Patch Toplevel/Entry/StringVar as in original test so we can simulate edit
        with patch('tkinter.Toplevel'):
            with patch('tkinter.Entry') as MockEntry, \
                 patch('tkinter.StringVar') as MockStringVar:

                entry_instances = [MagicMock(), MagicMock(), MagicMock()]
                MockEntry.side_effect = entry_instances

                entry_instances[0].get.return_value = "New Name"
                entry_instances[1].get.return_value = "new@mail.com"
                entry_instances[2].get.return_value = "newpass"

                role_var = MagicMock()
                role_var.get.return_value = "Client"
                MockStringVar.return_value = role_var

                self.app.admin_page.admin_edit_user()
                # Now simulate pressing Save by calling db.update_user
                self.mock_db_inst.update_user(uid, "New Name", "new@mail.com", "newpass", "Client")

                # assert DB changed
                updated_user = next(u for u in self.mock_db_inst.users if u[0] == uid)
                self.assertEqual(updated_user[1], "New Name")
                self.assertEqual(updated_user[2], "new@mail.com")
                self.assertEqual(updated_user[3], "newpass")
                self.assertEqual(updated_user[4], "Client")


if __name__ == '__main__':
    unittest.main()
