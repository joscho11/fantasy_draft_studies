import {
  BarChart,
  Callout,
  Card,
  CardBody,
  CardHeader,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  LineChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

const SLOTS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"];

const LEAGUE_Z = [
  -0.721, 0.594, -0.646, -0.673, -0.042, -0.022, 0.144, 0.62, -0.393, -0.234,
  0.842, 0.53,
];
const PUBLIC_Z = [
  -0.102, -0.006, 0.039, 0.056, 0.03, 0.03, 0.015, 0.025, -0.017, -0.045,
  -0.007, -0.019,
];
const LEAGUE_TOP6 = [0, 100, 33.3, 33.3, 66.7, 66.7, 33.3, 66.7, 33.3, 33.3, 66.7, 66.7];
const PUBLIC_TOP6 = [46.1, 49.8, 51.5, 52.8, 51.3, 50.9, 51.3, 50.3, 49.2, 48.8, 49.1, 49.0];

const YEAR_ROWS = [
  ["2023", "1", "Vacated", "Justin Jefferson", "1221.1", "10", "-1.07", "No"],
  ["2023", "2", "stn99", "Christian McCaffrey", "1466.6", "2", "+1.14", "Yes"],
  ["2023", "3", "GrantL69", "Ja'Marr Chase", "1181.0", "11", "-1.43", "No"],
  ["2023", "4", "MilanPandey", "Tyreek Hill", "1421.4", "4", "+0.73", "Yes"],
  ["2023", "5", "theted123", "Nick Chubb", "1177.5", "12", "-1.47", "No"],
  ["2023", "6", "JoScho", "Saquon Barkley", "1372.7", "6", "+0.29", "Yes"],
  ["2023", "7", "GarnerRandazzo", "Austin Ekeler", "1527.0", "1", "+1.69", "Yes"],
  ["2023", "8", "twp13", "Bijan Robinson", "1350.8", "7", "+0.10", "No"],
  ["2023", "9", "HHayes9", "Stefon Diggs", "1426.0", "3", "+0.78", "Yes"],
  ["2023", "10", "menglish8", "A.J. Brown", "1391.2", "5", "+0.46", "Yes"],
  ["2023", "11", "mpjuiceman24", "Derrick Henry", "1229.8", "9", "-0.99", "No"],
  ["2023", "12", "awf3", "Amon-Ra St. Brown", "1315.2", "8", "-0.22", "No"],
  ["2024", "1", "jacklevickas", "Christian McCaffrey", "1329.1", "8", "-0.35", "No"],
  ["2024", "2", "menglish8", "Tyreek Hill", "1472.0", "3", "+0.77", "Yes"],
  ["2024", "3", "theted123", "Bijan Robinson", "1234.5", "10", "-1.10", "No"],
  ["2024", "4", "GrantL69", "CeeDee Lamb", "1234.0", "11", "-1.10", "No"],
  ["2024", "5", "HHayes9", "Breece Hall", "1431.0", "6", "+0.45", "Yes"],
  ["2024", "6", "awf3", "Justin Jefferson", "1460.6", "4", "+0.68", "Yes"],
  ["2024", "7", "mpjuiceman24", "Amon-Ra St. Brown", "1347.4", "7", "-0.21", "No"],
  ["2024", "8", "GarnerRandazzo", "Ja'Marr Chase", "1454.6", "5", "+0.63", "Yes"],
  ["2024", "9", "twp13", "Jahmyr Gibbs", "1142.7", "12", "-1.82", "No"],
  ["2024", "10", "MilanPandey", "Garrett Wilson", "1295.9", "9", "-0.62", "No"],
  ["2024", "11", "JoScho", "Saquon Barkley", "1606.1", "1", "+1.83", "Yes"],
  ["2024", "12", "stn99", "A.J. Brown", "1481.9", "2", "+0.85", "Yes"],
  ["2025", "1", "stormduckkk", "Ja'Marr Chase", "1234.4", "9", "-0.74", "No"],
  ["2025", "2", "twp13", "Bijan Robinson", "1322.6", "6", "-0.13", "Yes"],
  ["2025", "3", "GarnerRandazzo", "CeeDee Lamb", "1428.6", "5", "+0.59", "Yes"],
  ["2025", "4", "stn99", "Saquon Barkley", "1101.0", "12", "-1.65", "No"],
  ["2025", "5", "awf3", "Jahmyr Gibbs", "1472.3", "4", "+0.89", "Yes"],
  ["2025", "6", "joshuasurprise", "Justin Jefferson", "1190.0", "10", "-1.04", "No"],
  ["2025", "7", "HHayes9", "Malik Nabers", "1189.5", "11", "-1.04", "No"],
  ["2025", "8", "theted123", "Derrick Henry", "1506.8", "2", "+1.13", "Yes"],
  ["2025", "9", "JoScho", "Josh Jacobs", "1322.3", "7", "-0.13", "No"],
  ["2025", "10", "GrantL69", "Amon-Ra St. Brown", "1262.1", "8", "-0.55", "No"],
  ["2025", "11", "MilanPandey", "Christian McCaffrey", "1589.3", "1", "+1.70", "Yes"],
  ["2025", "12", "menglish8", "Ashton Jeanty", "1483.0", "3", "+0.97", "Yes"],
];

const YEAR_TONE = YEAR_ROWS.map((row) => {
  if (row[2] === "JoScho") return "info" as const;
  if (row[2] === "Vacated") return "warning" as const;
  return undefined;
});

export default function CatonsvilleDraftOrder() {
  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Catonsville FF draft slots, 2023-2025</H1>
        <Text tone="secondary">
          Same study as the public Sleeper panel: 12-team completed snake,
          regular-season points only, within-league z-score and top-six. Half-PPR,
          14-round drafts, playoffs week 15. Three seasons, 36 team-seasons, 3
          observations per seat.
        </Text>
        <Row gap={8} wrap>
          <Pill size="sm">12-team snake</Pill>
          <Pill size="sm">Half-PPR</Pill>
          <Pill size="sm">n = 3 seasons</Pill>
          <Pill size="sm">Not causal</Pill>
        </Row>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="0/3" label="Slot 1 finished top six" tone="danger" />
        <Stat value="1/3" label="Slot 4 finished top six" tone="warning" />
        <Stat value="2/3" label="Slot 11 was #1 scorer" tone="success" />
        <Stat value="3/3" label="Slot 2 finished top six" />
      </Grid>

      <Callout tone="warning" title="Three seasons is a small room">
        The public study has 3,641 league-seasons. Slot effects there are a few
        hundredths of a z-score. This canvas can show whether the same seats were
        strong or weak in Catonsville. It cannot re-estimate those rates.
      </Callout>

      <Stack gap={8}>
        <H2>The seats the public study cares about</H2>
        <Text tone="secondary" size="small">
          Public numbers are 2018-2025, 3,641 leagues. Catonsville is 2023-2025.
        </Text>
        <Table
          striped
          headers={["Seat", "Public panel", "Catonsville, 3 yrs", "First-rounders here"]}
          columnAlign={["left", "left", "left", "left"]}
          rowTone={["danger", "warning", "success"]}
          rows={[
            [
              "Slot 1",
              "Weakest. z -0.10, top six 46.1%",
              "Worst. z -0.72, top six 0/3, mean finish 9.0",
              "Jefferson 2023, CMC 2024, Chase 2025. None made top six.",
            ],
            [
              "Slot 4",
              "Strongest. z +0.06, top six 52.8%",
              "Also weak. z -0.67, top six 1/3, mean finish 9.0",
              "Hill 2023 (4th). Lamb 2024 (11th). Saquon 2025 (12th).",
            ],
            [
              "Slot 11",
              "Average. z -0.01, top six 49.1%",
              "Best seat. z +0.84, two #1 scorers",
              "Henry 2023 (9th). Saquon 2024, JoScho #1. CMC 2025, Milan #1.",
            ],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>Regular-season points z-score by draft slot</H2>
        <LineChart
          categories={SLOTS}
          series={[
            { name: "Catonsville 2023-2025", data: LEAGUE_Z, tone: "info" },
            { name: "Public panel 2018-2025", data: PUBLIC_Z, tone: "neutral" },
          ]}
          beginAtZero={false}
          yMin={-1.2}
          yMax={1.2}
          height={260}
          referenceLines={[{ value: 0, label: "League average", tone: "neutral" }]}
        />
        <Text tone="tertiary" size="small">
          Z-score is (points minus league mean) / league SD, SD divided by 12,
          same formula as the study. Axis: draft slot vs within-league z-score.
          Source: Sleeper league 1383150363858722816 chain, seasons 2023-2025.
          Public line: fantasy_draft_order_study eda_slot_summary.csv, n=3,641.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>Top-six points rate by draft slot</H2>
        <BarChart
          categories={SLOTS}
          series={[
            { name: "Catonsville 2023-2025 (%)", data: LEAGUE_TOP6, tone: "info" },
            { name: "Public panel (%)", data: PUBLIC_TOP6, tone: "neutral" },
          ]}
          yMin={0}
          yMax={100}
          height={260}
          valueSuffix="%"
          referenceLines={[{ value: 50, label: "50%", tone: "neutral" }]}
        />
        <Text tone="tertiary" size="small">
          Top-six uses fractional credit for cutoff ties. Catonsville had no
          cutoff ties, so rates are 0/3, 1/3, 2/3, or 3/3. Public rates are
          percentages on 3,641 observations per slot.
        </Text>
      </Stack>

      <Stack gap={8}>
        <H2>Slot summary, three seasons pooled</H2>
        <Table
          striped
          stickyHeader
          headers={[
            "Slot",
            "Mean z",
            "Mean finish",
            "Mean pts",
            "Top six",
            "#1 scorer",
          ]}
          columnAlign={["right", "right", "right", "right", "right", "right"]}
          rowTone={[
            "danger",
            "success",
            undefined,
            "warning",
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            "success",
            undefined,
          ]}
          rows={[
            ["1", "-0.72", "9.00", "1261.5", "0/3", "0/3"],
            ["2", "+0.59", "3.67", "1420.4", "3/3", "0/3"],
            ["3", "-0.65", "8.67", "1281.4", "1/3", "0/3"],
            ["4", "-0.67", "9.00", "1252.1", "1/3", "0/3"],
            ["5", "-0.04", "7.33", "1360.2", "2/3", "0/3"],
            ["6", "-0.02", "6.67", "1341.1", "2/3", "0/3"],
            ["7", "+0.14", "6.33", "1354.6", "1/3", "1/3"],
            ["8", "+0.62", "4.67", "1437.4", "2/3", "0/3"],
            ["9", "-0.39", "7.33", "1297.0", "1/3", "0/3"],
            ["10", "-0.23", "7.33", "1316.4", "1/3", "0/3"],
            ["11", "+0.84", "3.67", "1475.1", "2/3", "2/3"],
            ["12", "+0.53", "4.33", "1426.7", "2/3", "0/3"],
          ]}
        />
        <Text tone="tertiary" size="small">
          Slot vs z-score Pearson r = +0.27 (R-squared 0.07, n=36). The public
          panel is flat (r = -0.0009). The positive slope here is slot 1 being
          terrible and slots 11-12 being strong, not a smooth later-is-better
          line.
        </Text>
      </Stack>

      <Card>
        <CardHeader trailing={<Pill size="sm">JoScho</Pill>}>
          Your three seats
        </CardHeader>
        <CardBody>
          <Table
            headers={["Year", "Slot", "Round 1", "Pts", "Finish", "Z", "Top six"]}
            columnAlign={["left", "right", "left", "right", "right", "right", "left"]}
            rows={[
              ["2023", "6", "Saquon Barkley", "1372.7", "6", "+0.29", "Yes"],
              ["2024", "11", "Saquon Barkley", "1606.1", "1", "+1.83", "Yes, #1"],
              ["2025", "9", "Josh Jacobs", "1322.3", "7", "-0.13", "No"],
            ]}
          />
          <Text tone="secondary" size="small">
            Two of three years you sat in a top-six points seat. 2024 slot 11 was
            the strongest season in this sample. 2025 slot 9 missed top six by
            one place.
          </Text>
        </CardBody>
      </Card>

      <Divider />

      <CollapsibleSection title="All 36 team-seasons" count={36}>
        <Stack gap={8}>
          <Text tone="secondary" size="small">
            Finish is regular-season points rank, 1 = highest scorer. JoScho
            rows are marked. 2023 slot 1 has no Sleeper owner on the roster.
          </Text>
          <Table
            striped
            stickyHeader
            headers={[
              "Year",
              "Slot",
              "Manager",
              "Round 1",
              "Pts",
              "Finish",
              "Z",
              "Top six",
            ]}
            columnAlign={[
              "left",
              "right",
              "left",
              "left",
              "right",
              "right",
              "right",
              "left",
            ]}
            rowTone={YEAR_TONE}
            rows={YEAR_ROWS}
          />
        </Stack>
      </CollapsibleSection>

      <Stack gap={6}>
        <H2>What this does not prove</H2>
        <Text tone="secondary">
          A causal effect of draft slot. Slot assignment here is not a randomized
          experiment. It does not speak to head-to-head record or playoffs.
          Sleeper points-for is the regular-season total, including the
          league-average extra games this league records. Keepers were set to a
          max of 1; none of these three drafts flagged a keeper pick. 2026 is
          pre-draft and is out.
        </Text>
      </Stack>
    </Stack>
  );
}
