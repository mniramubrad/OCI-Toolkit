<h1>OCI Cost Management</h1>

<p>
  Automation tools for extracting and analyzing OCI cost
  and usage data across multiple regions and compartments.
</p>

<h2>Features</h2>

<ul>
  <li>Daily cost and usage reporting</li>
  <li>Resource-level cost analysis</li>
  <li>SKU-based cost breakdown</li>
  <li>Multi-region and multi-compartment reporting</li>
  <li>Configurable reporting period</li>
  <li>Monthly CSV exports</li>
  <li>Automatic retries and resumable extraction</li>
  <li>Extraction summaries and error reporting</li>
</ul>

<h2>Requirements</h2>

<ul>
  <li>Python 3</li>
  <li>OCI Python SDK</li>
  <li>Appropriate IAM permissions for cost and usage data</li>
</ul>

<h2>Execution</h2>

<pre><code>python3 -u cost_final.py</code></pre>

<h2>Output</h2>

<pre><code>Final_Cost_Reports/
├── Cost_YYYY-MM.csv
├── Extraction_Summary.csv
├── Failed_Dates.csv
└── Daily/</code></pre>

<h2>Data Source</h2>

<p>
  Cost and usage data is retrieved through the OCI Usage API.
  The exported reports contain aggregated cost analysis data
  rather than raw FOCUS reports.
</p>
