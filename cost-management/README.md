<h1>OCI Cost Management</h1>

<p>
  A Python-based automation tool for extracting and analyzing
  Oracle Cloud Infrastructure (OCI) cost and usage data
  directly from OCI Cloud Shell.
</p>

<h2>Features</h2>

<ul>
  <li>Daily cost and usage reporting</li>
  <li>Resource-level cost analysis</li>
  <li>SKU-based cost breakdown</li>
  <li>Multi-region and multi-compartment reporting</li>
  <li>Configurable reporting period</li>
  <li>Monthly CSV exports</li>
  <li>Automatic pagination and retries</li>
  <li>Resumable daily extraction</li>
  <li>Extraction validation and error reporting</li>
</ul>

<h2>Prerequisites</h2>

<ul>
  <li>Access to OCI Cloud Shell</li>
  <li>Python 3</li>
  <li>OCI Python SDK</li>
  <li>Appropriate IAM permissions to access cost and usage data</li>
  <li>Sufficient storage space for generated reports</li>
</ul>

<h2>Authentication</h2>

<p>
  The script supports OCI Cloud Shell authentication using
  existing session credentials. No manual API key configuration
  is required when supported Cloud Shell credentials are available.
</p>

<h2>Execution</h2>

<p>
  Open OCI Cloud Shell, upload <code>cost_final.py</code>,
  and navigate to the directory containing the script.
</p>

<h3>Export a Specific Date Range</h3>

<pre><code>python3 -u cost_final.py \
  --start-date 2026-01-01 \
  --end-date 2026-02-01</code></pre>

<h3>Export Until the Current Date</h3>

<pre><code>python3 -u cost_final.py \
  --start-date 2026-01-01</code></pre>

<h3>Export with Execution Logs</h3>

<pre><code>python3 -u cost_final.py \
  --start-date 2026-01-01 \
  --end-date 2026-02-01 \
  2>&amp;1 | tee cost_export.log</code></pre>

<h2>Configuration Parameters</h2>

<table>
  <thead>
    <tr>
      <th align="left">Parameter</th>
      <th align="left">Description</th>
      <th align="left">Required</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>--start-date</code></td>
      <td>Reporting start date (YYYY-MM-DD)</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td><code>--end-date</code></td>
      <td>Reporting end date (exclusive)</td>
      <td>No</td>
    </tr>
    <tr>
      <td><code>--region</code></td>
      <td>OCI Usage API endpoint region</td>
      <td>No</td>
    </tr>
    <tr>
      <td><code>--profile</code></td>
      <td>OCI configuration profile</td>
      <td>No</td>
    </tr>
    <tr>
      <td><code>--output</code></td>
      <td>Custom output directory</td>
      <td>No</td>
    </tr>
  </tbody>
</table>

<p>
  If the end date is omitted, the current UTC date is used.
  The end date is exclusive, meaning the current incomplete
  day is excluded by default.
</p>

<h2>Exported Data</h2>

<ul>
  <li>Usage Date</li>
  <li>Usage Start and End Time</li>
  <li>Region</li>
  <li>Compartment Name</li>
  <li>Resource ID</li>
  <li>SKU Name</li>
  <li>Computed Quantity</li>
  <li>Computed Amount</li>
  <li>Attributed Usage</li>
  <li>Attributed Cost</li>
  <li>Currency</li>
</ul>

<h2>Output Structure</h2>

<pre><code>Final_Cost_Reports/
├── Cost_YYYY-MM.csv
├── Extraction_Summary.csv
├── Failed_Dates.csv
└── Daily/
    └── Cost_YYYY-MM-DD.csv</code></pre>

<h2>Validation</h2>

<p>
  Review the extraction summary after execution to verify
  the reporting period, record counts, regional distribution,
  and failed or missing dates.
</p>

<pre><code>ls -lh Final_Cost_Reports/
cat Final_Cost_Reports/Extraction_Summary.csv
cat Final_Cost_Reports/Failed_Dates.csv</code></pre>

<h2>Download Reports</h2>

<p>
  Compress the generated monthly reports and validation files
  into a single ZIP archive.
</p>

<pre><code>cd Final_Cost_Reports
zip ~/OCI_Cost_and_Usage.zip Cost_????-??.csv \
  Extraction_Summary.csv Failed_Dates.csv</code></pre>

<p>
  From OCI Cloud Shell, select <strong>Actions → Download</strong>
  and enter the following filename:
</p>

<pre><code>OCI_Cost_and_Usage.zip</code></pre>

<h2>Important Notes</h2>

<ul>
  <li>Reports are generated using the OCI Usage API.</li>
  <li>The API endpoint region does not restrict reporting to that region.</li>
  <li>Use a separate output directory for each OCI tenancy.</li>
  <li>Existing daily reports are reused when resuming extraction.</li>
  <li>Recent cost data may be subject to billing processing delays.</li>
  <li>Monthly CSV files may exceed Microsoft Excel's row limit.</li>
  <li>Generated reports may contain sensitive infrastructure and billing data.</li>
  <li>The exported data represents aggregated Cost Analysis data, not raw FOCUS reports.</li>
</ul>
