import analytics
import visualizer


def dashboard_menu(conn):
    """Data Science & Analytics Dashboard Menu."""
    while True:
        try:
            choice = int(input("""
=====================================================
      DATA SCIENCE & ANALYTICS DASHBOARD
=====================================================
1) Exploratory Data Analysis & Statistics (Pandas/NumPy)
2) Generate Visual Analytics Charts (Matplotlib/Seaborn)
3) Export Analytics Dataset to CSV
4) Return to Main Menu
Enter your choice (1-4) -> """).strip())
        except ValueError:
            print("\n[!] Invalid choice. Please enter a number (1-4).")
            continue

        if choice == 1:
            analytics.generate_eda_summary(conn)
        elif choice == 2:
            visualizer.generate_all_charts(conn)
        elif choice == 3:
            analytics.export_summary_csv(conn)
        elif choice == 4:
            print("\nReturning to Main Menu...")
            break
        else:
            print("\n[!] Invalid choice. Please select from 1 to 4.")
