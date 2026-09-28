"""
DATAFORGE — Foundation of training system
Purpose: Convert raw information into high-quality training material

Raw Data → Ingestion → Parsing → Normalization → Quality Analysis → Deduplication → Contamination Detection → Semantic Clustering → Safety Filtering → Data Mixture → Training Dataset

Quality: Q(x)=w1 Q_semantic + w2 Q_technical + w3 Q_novelty + w4 Q_source - w5 Q_risk
Bad → Discard, Medium → Auxiliary, High → Primary, Elite → Reasoning/curriculum
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import hashlib
import random

class DataQualityTier(Enum):
    BAD = "bad"
    MEDIUM = "medium"
    HIGH = "high"
    ELITE = "elite"

@dataclass
class DataSample:
    id: str
    content: str
    source: str
    modality: str  # text, code, math, image, audio, video, sensor, etc
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    tier: DataQualityTier = DataQualityTier.MEDIUM
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]

@dataclass
class QualityWeights:
    w_semantic: float = 0.3
    w_technical: float = 0.25
    w_novelty: float = 0.2
    w_source: float = 0.15
    w_risk: float = 0.1

class QualityEngine:
    """
    Q(x)=w1 Q_semantic + w2 Q_technical + w3 Q_novelty + w4 Q_source - w5 Q_risk
    """
    def __init__(self, weights: Optional[QualityWeights] = None):
        self.weights = weights or QualityWeights()

    def score(self, sample: DataSample) -> Tuple[float, DataQualityTier, Dict[str, float]]:
        # Mock scoring — in production would use models, heuristics, source reputation
        q_semantic = random.uniform(0.5, 1.0) if len(sample.content) > 50 else random.uniform(0.1, 0.5)
        q_technical = 0.9 if sample.modality in ["code","math","physics"] else random.uniform(0.3, 0.8)
        q_novelty = random.uniform(0.4, 0.9)
        # Source reputation
        trusted_sources = ["arxiv","github","wikipedia","textbook","simulation"]
        q_source = 0.9 if any(s in sample.source.lower() for s in trusted_sources) else random.uniform(0.2, 0.7)
        q_risk = random.uniform(0.0, 0.3) if "safe" in sample.metadata.get("safety","") else random.uniform(0.0, 0.6)

        q = (
            self.weights.w_semantic * q_semantic
            + self.weights.w_technical * q_technical
            + self.weights.w_novelty * q_novelty
            + self.weights.w_source * q_source
            - self.weights.w_risk * q_risk
        )
        q = max(0.0, min(1.0, q))

        if q < 0.3:
            tier = DataQualityTier.BAD
        elif q < 0.6:
            tier = DataQualityTier.MEDIUM
        elif q < 0.85:
            tier = DataQualityTier.HIGH
        else:
            tier = DataQualityTier.ELITE

        details = {
            "semantic": q_semantic,
            "technical": q_technical,
            "novelty": q_novelty,
            "source": q_source,
            "risk": q_risk,
            "total": q,
        }
        return q, tier, details

class DeduplicationEngine:
    def __init__(self):
        self.seen_hashes = set()

    def is_duplicate(self, sample: DataSample) -> bool:
        if sample.hash in self.seen_hashes:
            return True
        self.seen_hashes.add(sample.hash)
        return False

class ContaminationDetector:
    """
    Detect test set contamination
    """
    def __init__(self, test_hashes: Optional[set] = None):
        self.test_hashes = test_hashes or set()

    def is_contaminated(self, sample: DataSample) -> bool:
        # Check if sample hash overlaps with evaluation sets
        return sample.hash in self.test_hashes

class SemanticClustering:
    def cluster(self, samples: List[DataSample], k: int = 10) -> Dict[int, List[DataSample]]:
        # Mock clustering — in production use embeddings + k-means
        clusters = {i: [] for i in range(k)}
        for s in samples:
            cluster_id = hash(s.content) % k
            clusters[cluster_id].append(s)
        return clusters

class SafetyFilter:
    def is_safe(self, sample: DataSample) -> Tuple[bool, str]:
        unsafe_keywords = ["malicious", "exploit", "bioweapon"]
        content_lower = sample.content.lower()
        for kw in unsafe_keywords:
            if kw in content_lower:
                return False, f"Unsafe keyword: {kw}"
        return True, "Safe"

class DataMixture:
    def __init__(self):
        self.mixture = {
            "high": 0.5,
            "elite": 0.2,
            "medium": 0.2,
            "synthetic": 0.1,
        }

    def create_mixture(self, samples: List[DataSample]) -> List[DataSample]:
        # Sort by quality and create mixture per tier
        by_tier = {tier: [] for tier in DataQualityTier}
        for s in samples:
            by_tier[s.tier].append(s)

        # Sample according to mixture weights
        result = []
        # Elite for reasoning/curriculum
        result.extend(by_tier[DataQualityTier.ELITE][: int(len(samples)*self.mixture["elite"])])
        result.extend(by_tier[DataQualityTier.HIGH][: int(len(samples)*self.mixture["high"])])
        result.extend(by_tier[DataQualityTier.MEDIUM][: int(len(samples)*self.mixture["medium"])])
        return result

class DataForge:
    def __init__(self):
        self.quality_engine = QualityEngine()
        self.dedup = DeduplicationEngine()
        self.contamination = ContaminationDetector()
        self.clustering = SemanticClustering()
        self.safety = SafetyFilter()
        self.mixture = DataMixture()
        self.stats = {
            "ingested": 0,
            "deduplicated": 0,
            "contaminated": 0,
            "unsafe": 0,
            "bad": 0,
            "medium": 0,
            "high": 0,
            "elite": 0,
        }

    def ingest(self, raw_data: List[Dict[str, Any]]) -> List[DataSample]:
        samples = []
        for i, raw in enumerate(raw_data):
            sample = DataSample(
                id=f"sample_{i}",
                content=raw.get("content",""),
                source=raw.get("source","unknown"),
                modality=raw.get("modality","text"),
                metadata=raw.get("metadata",{}),
            )
            samples.append(sample)
        self.stats["ingested"] += len(samples)
        return samples

    def process(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[DataSample], Dict]:
        # Full pipeline: Ingestion → Parsing → Normalization → Quality → Deduplication → Contamination → Clustering → Safety → Mixture → Training Dataset
        samples = self.ingest(raw_data)

        # Normalization, parsing (mock)
        for s in samples:
            s.content = s.content.strip()

        # Quality analysis
        for s in samples:
            q, tier, details = self.quality_engine.score(s)
            s.quality_score = q
            s.tier = tier
            s.metadata["quality_details"] = details

        # Deduplication
        unique = []
        for s in samples:
            if not self.dedup.is_duplicate(s):
                unique.append(s)
            else:
                self.stats["deduplicated"] += 1

        # Contamination detection
        clean = []
        for s in unique:
            if not self.contamination.is_contaminated(s):
                clean.append(s)
            else:
                self.stats["contaminated"] += 1

        # Safety filtering
        safe = []
        for s in clean:
            is_safe, reason = self.safety.is_safe(s)
            if is_safe:
                safe.append(s)
            else:
                self.stats["unsafe"] += 1

        # Tier counts
        for s in safe:
            if s.tier == DataQualityTier.BAD:
                self.stats["bad"] += 1
            elif s.tier == DataQualityTier.MEDIUM:
                self.stats["medium"] += 1
            elif s.tier == DataQualityTier.HIGH:
                self.stats["high"] += 1
            elif s.tier == DataQualityTier.ELITE:
                self.stats["elite"] += 1

        # Discard BAD
        filtered = [s for s in safe if s.tier != DataQualityTier.BAD]

        # Semantic clustering
        clusters = self.clustering.cluster(filtered, k=5)

        # Data mixture → Training Dataset
        training_dataset = self.mixture.create_mixture(filtered)

        return training_dataset, {
            "stats": self.stats,
            "clusters": {k: len(v) for k,v in clusters.items()},
            "final_size": len(training_dataset),
        }

if __name__ == "__main__":
    forge = DataForge()
    raw = [
        {"content": "The transformer architecture uses self-attention mechanism...", "source": "arxiv", "modality": "text"},
        {"content": "def quicksort(arr): ...", "source": "github", "modality": "code"},
        {"content": "P=VI for electrical power, S=P+jQ apparent power", "source": "textbook", "modality": "physics"},
        {"content": "short", "source": "unknown", "modality": "text"},
        {"content": "The transformer architecture uses self-attention mechanism...", "source": "arxiv", "modality": "text"},  # duplicate
    ]
    dataset, report = forge.process(raw)
    print(f"Final dataset size: {len(dataset)}")
    print(f"Stats: {report['stats']}")
    for s in dataset:
        print(f"  {s.id} tier={s.tier.value} Q={s.quality_score:.2f} hash={s.hash}")
