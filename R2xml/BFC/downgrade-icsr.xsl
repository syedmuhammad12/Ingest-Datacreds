<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xmlns:fo="http://www.w3.org/1999/XSL/Format" 
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" 
	xmlns:mif="urn:hl7-org:v3/mif"
	exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<xsl:include href="downgrade.xsl"/>
	<xsl:include href="downgrade-m.xsl"/>
	<xsl:include href="downgrade-a1.xsl"/>
	<xsl:include href="downgrade-a2.xsl"/>
	<xsl:include href="downgrade-a3.xsl"/>
	<xsl:include href="downgrade-b1.xsl"/>
	<xsl:include href="downgrade-b2.xsl"/>
	<xsl:include href="downgrade-b3.xsl"/>
	<xsl:include href="downgrade-b4.xsl"/>
	<xsl:include href="downgrade-b5.xsl"/>
	
	<xsl:output 
	method="xml" 
	version="1.0" 
	encoding="UTF-8"
	omit-xml-declaration="no"
	doctype-system="http://eudravigilance.ema.europa.eu/dtd/icsr21xml.dtd"
	indent="yes" />
	<xsl:strip-space elements="*"/> 
	
	
	<!-- ICH ICSR : 
	E2B(R3): root element "PORR_IN049006UV"
	E2B(R2): root element "ichicsr"
	-->
	<xsl:template match="/">
		<ichicsr lang="en" >
			<xsl:apply-templates select="hl7:MCCI_IN200100UV01"/>
			<xsl:apply-templates select="hl7:MCCI_IN200100UV01/hl7:PORR_IN049016UV/hl7:controlActProcess/hl7:subject/hl7:investigationEvent" mode="safetyreport"/>
		</ichicsr>
	</xsl:template>
	
	<!-- ICSR Backbone -->
	<xsl:template match="hl7:investigationEvent" mode="safetyreport">
		<safetyreport>
		<safetyreportversion/>
			<!-- A.1 Safety Report -->
			<xsl:call-template name="safetyreportheader"/>
			<!-- A.2 Primary Sources, sorted to have the one for regulatory purposes first -->
			<xsl:apply-templates select="hl7:outboundRelationship/hl7:relatedInvestigation[hl7:code/@code=$SourceReport]/hl7:subjectOf2/hl7:controlActEvent/hl7:author/hl7:assignedEntity" mode="primary-source">
				<xsl:sort select = "../../../../../hl7:priorityNumber/@value" order="descending"/>  
			</xsl:apply-templates>
			<!-- A.3.1 Sender -->
			<sender>
				<xsl:apply-templates select="hl7:subjectOf1/hl7:controlActEvent/hl7:author/hl7:assignedEntity" mode="sender"/>
			</sender>
			<!-- A.3.2 Receiver -->
			<receiver/>
			<patient>
				<!-- B.1 Patient -->
				<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole" mode="patient"/>
				<!-- B.2 Reaction -->
				<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:observation[hl7:code/@code=$Reaction]" mode="reaction"/>
				<!-- B.3 Test -->
				<xsl:apply-templates select="hl7:component/hl7:adverseEventAssessment/hl7:subject1/hl7:primaryRole/hl7:subjectOf2/hl7:organizer[hl7:code/@code=$TestsAndProceduresRelevantToTheInvestigation]/hl7:component/hl7:observation" mode="test"/>
				<!-- B.4 Drug -->
				<xsl:call-template name="Drug" />
				<!-- B.5 Summary -->
				<xsl:apply-templates select="." mode="summary"/>
			</patient>
		</safetyreport>
	</xsl:template>
	
</xsl:stylesheet>
