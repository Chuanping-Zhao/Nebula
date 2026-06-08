from nebula.io import create_nebula


data = create_nebula(
    features_file="demodata/inputfile_format/feature_intensity.csv",
    annotations_file="demodata/inputfile_format/annoations.csv",
    metadata_file="demodata/inputfile_format/sampleInfo_metadata.csv",
    features_id_col="ID",
    sample_id_col="Run",
)

print(data.features.shape)
print(data.annotations.shape)
print(data.metadata.shape)
print(data.features.head())
