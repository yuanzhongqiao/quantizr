
package quanta.rest.request;

import quanta.rest.request.base.RequestBase;

public class ExportRequest extends RequestBase {
	private String nodeId;
	// must be file extension, and selects which type of file to export
	private String exportExt;
	private String fileName;
	private boolean includeToc;
	private boolean includeMetaComments;
	private String contentType;
	private boolean includeIDs;
	private boolean dividerLine;
	private boolean updateHeadings;
	private boolean threadAsPDF;
	private boolean includeOwners;
	private boolean numberedFigures;
	private String contentWidth;

	public ExportRequest() {}

	public String getNodeId() {
		return this.nodeId;
	}

	public String getExportExt() {
		return this.exportExt;
	}

	public String getFileName() {
		return this.fileName;
	}

	public boolean isIncludeToc() {
		return this.includeToc;
	}

	public boolean isIncludeMetaComments() {
		return includeMetaComments;
	}

	public void setIncludeMetaComments(boolean includeMetaComments) {
		this.includeMetaComments = includeMetaComments;
	}

	public boolean isIncludeIDs() {
		return this.includeIDs;
	}

	public boolean isDividerLine() {
		return this.dividerLine;
	}

	public boolean isUpdateHeadings() {
		return this.updateHeadings;
	}

	public void setNodeId(final String nodeId) {
		this.nodeId = nodeId;
	}

	public void setExportExt(final String exportExt) {
		this.exportExt = exportExt;
	}

	public void setFileName(final String fileName) {
		this.fileName = fileName;
	}

	public void setIncludeToc(final boolean includeToc) {
		this.includeToc = includeToc;
	}

	public void setIncludeIDs(final boolean includeIDs) {
		this.includeIDs = includeIDs;
	}

	public void setDividerLine(final boolean dividerLine) {
		this.dividerLine = dividerLine;
	}

	public void setUpdateHeadings(final boolean updateHeadings) {
		this.updateHeadings = updateHeadings;
	}

	public String getContentType() {
		return contentType;
	}

	public void setContentType(String contentType) {
		this.contentType = contentType;
	}

	public boolean isThreadAsPDF() {
		return threadAsPDF;
	}

	public void setThreadAsPDF(boolean threadAsPDF) {
		this.threadAsPDF = threadAsPDF;
	}

	public boolean isIncludeOwners() {
		return includeOwners;
	}

	public void setIncludeOwners(boolean includeOwners) {
		this.includeOwners = includeOwners;
	}

	public boolean isNumberedFigures() {
		return numberedFigures;
	}

	public void setNumberedFigures(boolean numberedFigures) {
		this.numberedFigures = numberedFigures;
	}

	public String getContentWidth() {
		return contentWidth;
	}

	public void setContentWidth(String contentWidth) {
		this.contentWidth = contentWidth;
	}
}
