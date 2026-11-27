<h1>OCI Inventory</h1>

<p>
  Automation scripts for collecting and exporting resource
  inventory and utilization metrics across OCI regions
  and compartments.
</p>

<h2>Features</h2>

<ul>
  <li>Compute instance inventory</li>
  <li>Block and boot volume inventory</li>
  <li>Block and boot volume backup inventory</li>
  <li>CPU and memory utilization for the last 90 days</li>
  <li>Multi-region and multi-compartment support</li>
  <li>Excel and CSV reporting</li>
</ul>

<h2>Requirements</h2>

<ul>
  <li>Python 3</li>
  <li>OCI Python SDK</li>
  <li>OpenPyXL</li>
  <li>Appropriate OCI IAM permissions</li>
</ul>

<h2>Execution</h2>

<pre><code>python3 -u oci_export.py
python3 generate_excel.py</code></pre>

<h2>Output</h2>

<pre><code>Final_Reports/OCI_Inventory.xlsx</code></pre>
