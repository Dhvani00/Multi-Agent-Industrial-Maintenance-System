from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MaintenanceRetriever:
    """Lightweight TF-IDF retrieval over maintenance descriptions."""

    def __init__(self, maintenance_df):
        self.records = maintenance_df.copy().fillna("")
        self.texts = (
            self.records["category"].astype(str) + " " +
            self.records["description"].astype(str) + " " +
            self.records["action_taken"].astype(str)
        ).tolist()
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(self.texts) if self.texts else None

    def search(self, query, turbine_id=None, top_k=4):
        if self.matrix is None or len(self.records) == 0:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        candidates = self.records.copy()
        candidates["_score"] = scores
        if turbine_id:
            candidates = candidates[candidates["turbine_id"] == turbine_id]
        candidates = candidates.sort_values("_score", ascending=False).head(top_k)
        results = []
        for _, row in candidates.iterrows():
            if float(row["_score"]) <= 0:
                continue
            results.append({
                "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
                "turbine_id": row["turbine_id"],
                "category": row["category"],
                "description": row["description"],
                "action_taken": row["action_taken"],
                "retrieval_score": round(float(row["_score"]), 3),
            })
        return results
