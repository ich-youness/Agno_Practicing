import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.evaluation.single_table import evaluate_quality, run_diagnostic, get_column_plot
from faker import Faker
import random
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Load CSV
csv_path = r"D:\Agno\SDV\E-Commerce Dataset.csv"
df = pd.read_csv(csv_path)

# Global Variables
metadata = None
synthetic_data = None
quality_report_result = None


def synthetize_data(df):
    global metadata, synthetic_data
    metadata = Metadata.detect_from_dataframe(df)
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(df)
    synthetic_data = synthesizer.sample(num_rows=len(df))
    synthetic_data.to_csv("synthetic_ecommerce.csv", index=False)


def synthetize_with_variety(df):
    global metadata, synthetic_data
    metadata = Metadata.detect_from_dataframe(df)
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(df)
    synthetic_data = synthesizer.sample(num_rows=len(df)).sample(frac=1).reset_index(drop=True)
    synthetic_data.to_csv("synthetic_variety.csv", index=False)
    print(" Synthetic data with realistic variety generated.")


def synthetize_with_narratives(df):
    global metadata, synthetic_data
    metadata = Metadata.detect_from_dataframe(df)
    narrative_cols = [col for col in df.columns if df[col].dtype == 'object' and df[col].str.len().mean() > 20]
    df_no_narrative = df.drop(columns=narrative_cols)
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(df_no_narrative)
    synthetic_data = synthesizer.sample(num_rows=len(df))
    faker = Faker()
    for col in narrative_cols:
        synthetic_data[col] = [faker.paragraph(nb_sentences=random.randint(2, 5)) for _ in range(len(synthetic_data))]
    synthetic_data.to_csv("synthetic_narrative.csv", index=False)
    print(" Synthetic data with narrative fields generated.")


def diagnostic_report():
    report = run_diagnostic(real_data=df, synthetic_data=synthetic_data, metadata=metadata)
    print("\n Diagnostic Report (Data Structure):")
    print(report.get_details(property_name='Data Structure'))


def quality_report():
    global quality_report_result
    quality_report_result = evaluate_quality(real_data=df, synthetic_data=synthetic_data, metadata=metadata)
    print(f"\n Overall Quality Score: {quality_report_result.get_score():.2%}")


def column_plot():
    if quality_report_result is None:
        print(" Quality report not generated yet. Generating now...")
        quality_report()
    print('\nColumns from highest to lowest quality score:')
    print('-----------------------------------------------------------')
    print(quality_report_result.get_details('Column Shapes'))


def visualize_data():
    if metadata is None or synthetic_data is None:
        print("Generate synthetic data first.")
        return
    try:
        fig = get_column_plot(
            real_data=df,
            synthetic_data=synthetic_data,
            column_name='PreferedOrderCat',
            metadata=metadata
        )
        fig.show()
    except Exception as e:
        print(f" Error displaying plot: {e}")


def run():
    print("""
 What is the objective of the Data you want to synthetize? (Type the number):
    1. Schema replication
    2. Realism + variety
    3. Narrative fields (e.g., reviews, support tickets)
    Type 'help' to see a detailed explanation.
""")

    choice = input("Your choice: ").strip()

    if choice == 'help':
        print("""
 Help:
    1. Schema replication: Match structure/distribution of the original dataset.
    2. Realism + variety: Capture patterns, but add randomness for diversity.
    3. Narrative fields: Generate human-readable text for long-form fields.
""")
        return run()

    elif choice == '1':
        print(" Schema replication selected.")
        synthetize_data(df)

    elif choice == '2':
        print(" Realism + variety selected.")
        synthetize_with_variety(df)

    elif choice == '3':
        print(" Narrative field generation selected.")
        synthetize_with_narratives(df)

    else:
        print(" Invalid input.")
        return run()

    while True:
        print("""
✨ What do you want to do next?
    1. View the diagnostic report
    2. View the quality report
    3. View column-wise quality scores
    4. Visualize a column comparison
    5. Exit
""")
        next_step = input("Your choice: ").strip()
        if next_step == '1':
            diagnostic_report()
        elif next_step == '2':
            quality_report()
        elif next_step == '3':
            column_plot()
        elif next_step == '4':
            visualize_data()
        elif next_step == '5':
            print(" Done.")
            break
        else:
            print(" Invalid choice.")


if __name__ == "__main__":
    run()
