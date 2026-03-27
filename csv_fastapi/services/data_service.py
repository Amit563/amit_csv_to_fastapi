import pandas as pd

class DataService:
    def __init__(self, file_path: str):
        self.df = pd.read_csv(file_path)
        self._clean_data()

    def _clean_data(self):
        # Clean column names
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Create ID column if not exists
        if "id" not in self.df.columns:
            self.df["id"] = self.df.index

        # Handle missing values
        num_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        cat_cols = self.df.select_dtypes(include=['object']).columns

        self.df[num_cols] = self.df[num_cols].fillna(0)
        self.df[cat_cols] = self.df[cat_cols].fillna("")

    # ✅ Get by student_id (STRING)
    def get_by_student_id(self, student_id: str):
        return self.df[self.df["student_id"] == student_id]

    # ✅ Get by numeric id
    def get_by_id(self, id: int):
        return self.df[self.df["id"] == id]

    def get_all(self):
        return self.df

    def filter_data(self, column: str, value: str):
        if column not in self.df.columns:
            raise Exception("Column not found")

        return self.df[self.df[column].astype(str) == value]

    def search_data(self, column: str, keyword: str):
        if column not in self.df.columns:
            raise Exception("Column not found")

        return self.df[self.df[column].astype(str).str.contains(keyword, case=False)]


# ✅ FIX: pass file_path here
data_service = DataService(r"services\students_complete.csv")