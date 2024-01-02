<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - B.4 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			18/11/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion, EU specific data fields & bug fixes
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">


	<!-- Drug (main): 
	E2B(R2): element "drug"
	E2B(R3): element "drugInformation" called from upgrade-b1
	-->
	<xsl:template match="drug" mode="main">
				<component typeCode="COMP">
					<substanceAdministration moodCode="EVN" classCode="SBADM">
						<id root="DID{position()}"/>
						<consumable typeCode="CSM">
							<instanceOfKind classCode="INST">
								<kindOfProduct classCode="MMAT" determinerCode="KIND">
									<!-- B.4.k.2.2 Medicinal Product Name as Reported by the Primary Source -->
									<code/>
									<name>
										<xsl:choose>
												<xsl:when test="string-length(medicinalproduct) > 0"><xsl:value-of select="medicinalproduct"/></xsl:when>
												<xsl:otherwise>
													<xsl:for-each select="./activesubstance/activesubstancename">
														<xsl:value-of select="concat(., substring(',', 2 - (position() != last())))" />
													</xsl:for-each>														
													</xsl:otherwise>
										</xsl:choose>
									</name>
									<asManufacturedProduct classCode="MANU">
										<!-- B.4.k.3 Authorization Info on Drug -->
										<xsl:if test="string-length(drugauthorizationnumb) > 0 or string-length(drugauthorizationholder) > 0 or string-length(drugauthorizationcountry) > 0">
											<subjectOf typeCode="SBJ">
												<approval classCode="CNTRCT" moodCode="EVN">
													<xsl:if test="string-length(drugauthorizationnumb) > 0">
														<id extension="{drugauthorizationnumb}" root="{$oidAuthorisationNumber}"/>
													</xsl:if>
													<xsl:if test="string-length(drugauthorizationholder) > 0">
														<holder typeCode="HLD">
															<role classCode="HLD">
																<playingOrganization classCode="ORG" determinerCode="INSTANCE">
																	<name><xsl:value-of select="drugauthorizationholder"/></name>
																</playingOrganization>
															</role>
														</holder>
													</xsl:if>
													<xsl:if test="string-length(drugauthorizationcountry) > 0">
														<author typeCode="AUT">
															<territorialAuthority classCode="TERR">
																<territory classCode="NAT" determinerCode="INSTANCE">
																	<code codeSystem="{$oidISOCountry}" code="{drugauthorizationcountry}"/>
																</territory>
															</territorialAuthority>
														</author>
													</xsl:if>
												</approval>
											</subjectOf>
										</xsl:if>
									</asManufacturedProduct>
									<!-- B.4.k.2.3.r Active Ingredient -->
									<xsl:apply-templates select="activesubstance"/>
								</kindOfProduct>
								<!-- B.4.k.2.4 Identification of the Country where the Drug was Obtained -->
								<xsl:if test="string-length(obtaindrugcountry) > 0">
									<subjectOf typeCode="SBJ">
										<productEvent classCode="ACT" moodCode="EVN">
											<code code="{$RetailSupply}" codeSystem="{$oidActionPerformedCode}"/>
											<performer typeCode="PRF">
												<assignedEntity classCode="ASSIGNED">
													<representedOrganization classCode="ORG" determinerCode="INSTANCE">
														<addr>
															<country><xsl:value-of select="obtaindrugcountry"/></country>
														</addr>
													</representedOrganization>
												</assignedEntity>
											</performer>
										</productEvent>
									</subjectOf>
								</xsl:if>
							</instanceOfKind>
						</consumable>
					<!--	<xsl:for-each select="../reaction[1]">
							<xsl:if test="string-length(reactionfirsttime) > 0">
								<outboundRelationship1 typeCode="SAS">
									<pauseQuantity value="{reactionfirsttime}">
										<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="reactionfirsttimeunit"/></xsl:call-template></xsl:attribute>
									</pauseQuantity>
									<actReference classCode="ACT" moodCode="EVN">
										<id extension="RID1"/>
									</actReference>
								</outboundRelationship1>
							</xsl:if>
							<xsl:if test="string-length(reactionlasttime)>0">
								<outboundRelationship1 typeCode="SAE">
									<pauseQuantity value="{reactionlasttime}">
										<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="reactionlasttimeunit"/></xsl:call-template></xsl:attribute>
									</pauseQuantity>
									<actReference classCode="ACT" moodCode="EVN">
										<id extension="RID1"/>
									</actReference>
								</outboundRelationship1>
							</xsl:if>
						</xsl:for-each> -->
						<!-- B.4.k.4 Dosage -->
						<!-- <xsl:if test="string-length(drugstructuredosagenumb) > 0 or string-length(drugintervaldosageunitnumb) > 0 or string-length(drugdosagetext) > 0 or string-length(drugadministrationroute) > 0 or string-length(drugstartdate) > 0 or string-length(drugenddate) > 0"> -->
							<outboundRelationship2 typeCode="COMP">
								<substanceAdministration classCode="SBADM" moodCode="EVN">
									<!-- B.4.k.4.r.10 Dosage Text -->
									<xsl:if test="string-length(drugdosagetext) > 0">
										<text><xsl:value-of select="drugdosagetext"/></text>
									</xsl:if>
									<!-- B.4.k.4.r.4 Dosage Unit Number and Interval -->
									<!-- version 2.0 edit to fix SXPR_TS error  on missing PIVL_TS -->
									<xsl:if test="string-length(drugintervaldosageunitnumb) > 0 or string-length(drugstartdate) > 0 or string-length(drugenddate) > 0 or string-length(drugtreatmentduration ) > 0 ">
										<effectiveTime xsi:type="SXPR_TS">
										<xsl:choose>
											<xsl:when test="string-length(drugintervaldosageunitnumb) > 0">
												<comp xsi:type="PIVL_TS">
													<period value="{drugintervaldosageunitnumb}">
														<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="drugintervaldosagedefinition"/></xsl:call-template></xsl:attribute>
													</period>
												</comp>
											</xsl:when>
											<xsl:otherwise>
											<comp xsi:type="PIVL_TS">
													<period nullFlavor="NI"/>
											</comp>
											</xsl:otherwise>
											</xsl:choose>
											<xsl:choose>
												<xsl:when test="string-length(drugstartdate) = 0 or string-length(drugenddate) = 0 or string-length(drugtreatmentduration) = 0">
													<comp xsi:type="IVL_TS" operator="A">
														<xsl:if test="string-length(drugstartdate) > 0">
															<low value="{drugstartdate}"/>
														</xsl:if>
														<xsl:if test="string-length(drugtreatmentduration) > 0 and string-length(drugenddate) = 0">
															<width value="{drugtreatmentduration}">
																<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="drugtreatmentdurationunit"/></xsl:call-template></xsl:attribute>
															</width>
														</xsl:if>
														<xsl:if test="string-length(drugenddate) > 0">
															<high value="{drugenddate}"/>
														</xsl:if>
													</comp>
												</xsl:when>
												<xsl:otherwise>
													<comp xsi:type="IVL_TS" operator="A">
														<low value="{drugstartdate}"/>
														<high value="{drugenddate}"/>
													</comp>
													<comp xsi:type="IVL_TS" operator="A">
														<width value="{drugtreatmentduration}">
															<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="drugtreatmentdurationunit"/></xsl:call-template></xsl:attribute>
														</width>
													</comp>
												</xsl:otherwise>
											</xsl:choose>
										</effectiveTime>
									</xsl:if>
									<!-- B.4.k.4.r.12 Route of Administration -->
									<xsl:if test="string-length(drugadministrationroute) > 0">
										<routeCode code="{drugadministrationroute}" codeSystem="{$oidICHRoute}" codeSystemVersion="{$oidICHRouteCSV}"/>
									</xsl:if>
									<!-- B.4.k.4.r.2 Dose Quantity -->
									<xsl:if test="string-length(drugstructuredosagenumb) > 0 or string-length(drugstructuredosageunit) > 0">
										<doseQuantity>
											<xsl:choose>
												<xsl:when test="string-length(drugseparatedosagenumb) > 0">
													<xsl:attribute name="value"><xsl:value-of select="drugstructuredosagenumb * drugseparatedosagenumb"/></xsl:attribute>
												</xsl:when>
												<xsl:otherwise>
													<xsl:attribute name="value"><xsl:value-of select="drugstructuredosagenumb"/></xsl:attribute>
												</xsl:otherwise>
											</xsl:choose>
											<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="drugstructuredosageunit"/></xsl:call-template></xsl:attribute>
										</doseQuantity>
									</xsl:if>
									<!-- B.4.k.4.r.9, 11 Batch Number and Dose Form -->
									<xsl:if test="string-length(drugbatchnumb) > 0 or string-length(drugdosageform) > 0">
										<consumable typeCode="CSM">
											<instanceOfKind classCode="INST">
												<productInstanceInstance classCode="MMAT" determinerCode="INSTANCE">
													<id nullFlavor="NI"/>
													<lotNumberText><xsl:value-of select="drugbatchnumb"/></lotNumberText>
												</productInstanceInstance>
												<kindOfProduct classCode="MMAT" determinerCode="KIND">
													<formCode>
														<originalText>
															<xsl:value-of select="drugdosageform"/>
														</originalText>
													</formCode>
												</kindOfProduct>
											</instanceOfKind>
										</consumable>
									</xsl:if>
									<!-- B.4.k.4.r.13 Parent Route -->
									<xsl:if test="string-length(drugparadministration) > 0">
										<inboundRelationship typeCode="REFR">
											<observation moodCode="EVN" classCode="OBS">
												<code code="{$ParentRouteOfAdministration}" codeSystem="{$oidObservationCode}"/>
												<value xsi:type="CE" code="{drugparadministration}" codeSystem="{$oidICHRoute}"/>
											</observation>
										</inboundRelationship>
									</xsl:if>
								</substanceAdministration>
							</outboundRelationship2>
						<!-- </xsl:if> -->
						<!-- B.4.k.5 Cumulative Dosage -->
						<xsl:if test="string-length(drugcumulativedosagenumb) > 0">
							<outboundRelationship2 typeCode="SUMM">
								<observation moodCode="EVN" classCode="OBS">
									<code code="{$CumulativeDoseToReaction}" codeSystem="{$oidObservationCode}"/>
									<value xsi:type="PQ" value="{drugcumulativedosagenumb}">
										<xsl:attribute name="unit">
											<xsl:choose>
												<xsl:when test="string-length(drugcumulativedosageunit) > 0"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="drugcumulativedosageunit"/></xsl:call-template></xsl:when>
												<xsl:otherwise>1</xsl:otherwise>
											</xsl:choose>
										</xsl:attribute>
									</value>
								</observation>
							</outboundRelationship2>
						</xsl:if>
						<!-- B.4.k.6 Gestation Period at Time of Exposure -->
						<xsl:if test="string-length(reactiongestationperiod) > 0">
							<outboundRelationship2 typeCode="PERT">
								<observation moodCode="EVN" classCode="OBS">
									<code code="{$GestationPeriod}" codeSystem="{$oidObservationCode}"/>
									<value xsi:type="PQ" value="{reactiongestationperiod}">
										<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="reactiongestationperiodunit"/></xsl:call-template></xsl:attribute>
									</value>
								</observation>
							</outboundRelationship2>
						</xsl:if>
						<!-- B.4.k.10.2 Additional Info on Drug-->
						<xsl:if test="string-length(drugadditional) > 0">
							<outboundRelationship2 typeCode="REFR">
								<observation moodCode="EVN" classCode="OBS">
									<code code="{$AdditionalInformation}" codeSystem="{$oidObservationCode}"/>
									<value xsi:type="ST"><xsl:value-of select="drugadditional"/></value>
								</observation>
							</outboundRelationship2>
						</xsl:if>
						<!-- B.4.k.9.i.4 Recurrance of Reaction -->
						<xsl:apply-templates select="drugrecurrence" mode="recur"/>
						<!-- B.4.k.7.r Indication for Use in the Case from Primary Source -->
						<xsl:if test="string-length(drugindication) > 0">
							<inboundRelationship typeCode="RSON">
								<observation moodCode="EVN" classCode="OBS">
									<code code="{$Indication}" codeSystem="{$oidObservationCode}"/>
									<value xsi:type="CE">
										<xsl:if test="string-length(drugindicationmeddraversion) > 0">
											<xsl:attribute name="codeSystem"><xsl:value-of select="$oidMedDRA"/></xsl:attribute>
											<xsl:attribute name="codeSystemVersion"><xsl:value-of select="drugindicationmeddraversion"/></xsl:attribute>
										</xsl:if>
										<xsl:choose>
											<xsl:when test="number(drugindication)">
												<xsl:attribute name="code"><xsl:value-of select="drugindication"/></xsl:attribute>
											</xsl:when>
											<xsl:otherwise>
												<originalText>
													<xsl:value-of select="drugindication"/>
													<xsl:if test="string-length(drugindicationmeddraversion) > 0">(<xsl:value-of select="drugindicationmeddraversion"/>)</xsl:if>
												</originalText>
											</xsl:otherwise>
										</xsl:choose>
									</value>
									<performer typeCode="PRF">
										<assignedEntity classCode="ASSIGNED">
											<code code="{$SourceReporter}" codeSystem="{$oidAssignedEntityRoleCode}"/>
										</assignedEntity>
									</performer>
									<outboundRelationship1 typeCode="REFR">
										<actReference classCode="SBADM" moodCode="EVN">
											<id root="DID{position()}"/>
										</actReference>
									</outboundRelationship1>
								</observation>
							</inboundRelationship>
						</xsl:if>
						<!-- B.4.k.16 Action(s) taken with Drug -->
						<xsl:if test="string-length(actiondrug) > 0">
							<inboundRelationship typeCode="CAUS">
								<act classCode="ACT" moodCode="EVN">
									<xsl:choose>
										<xsl:when test="actiondrug = 5"><code code="0" codeSystem="{$oidActionTaken}" codeSystemVersion="{$oidActionTakenCSV}"/></xsl:when>
										<xsl:when test="actiondrug = 6"><code code="9" codeSystem="{$oidActionTaken}" codeSystemVersion="{$oidActionTakenCSV}"/></xsl:when>
										<xsl:otherwise><code code="{actiondrug}" codeSystem="{$oidActionTaken}" codeSystemVersion="{$oidActionTakenCSV}"/></xsl:otherwise>
									</xsl:choose>
								</act>
							</inboundRelationship>
						</xsl:if>
					</substanceAdministration>
				</component>
	</xsl:template>
	
	<!-- Active Substance : 
	E2B(R2): element "activesubstance"
	E2B(R3): element "drugInformation"
	-->
	<xsl:template match="activesubstance">
		<!-- B.4.k.2.3.r Active Ingredient -->
		<ingredient classCode="ACTI">
			<ingredientSubstance classCode="MMAT" determinerCode="KIND">
				<name><xsl:value-of select="activesubstancename"/></name>
			</ingredientSubstance>
		</ingredient>
	</xsl:template>	
	
	<!-- Did Recur on Readministration: 
	E2B(R2): element "recur"
	E2B(R3): element ""
	-->
	<xsl:template match="drugrecurrence" mode="recur">
		<xsl:if test="../drugrecurreadministration = 1 or ../drugrecurreadministration = 2">
			<outboundRelationship2 typeCode="PERT">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$RecurranceOfReaction}" codeSystem="{$oidObservationCode}"/>
					<xsl:choose>
						<xsl:when test="../drugrecurreadministration = 1"><value xsi:type="CE" code="1" codeSystem="{$oidRechallenge}" codeSystemVersion="{$oidRechallengeCSV}"/></xsl:when>
						<xsl:when test="../drugrecurreadministration = 2"><value xsi:type="CE" code="2" codeSystem="{$oidRechallenge}" codeSystemVersion="{$oidRechallengeCSV}"/></xsl:when>
					</xsl:choose>
					<xsl:variable name="reaction" select="drugrecuraction"/>
					<xsl:variable name="rid">
						<xsl:for-each select="../../reaction">
							<xsl:if test="reactionmeddrallt = $reaction or primarysourcereaction = $reaction">RID<xsl:value-of select="position()"/></xsl:if>
						</xsl:for-each>
					</xsl:variable>
					<xsl:if test="string-length($rid) > 0">
						<outboundRelationship1 typeCode="REFR">
							<actReference moodCode="EVN" classCode="ACT">
								<id root="{$rid}"/>
							</actReference>
						</outboundRelationship1>
					</xsl:if>
				</observation>
			</outboundRelationship2>
		</xsl:if>
	</xsl:template>
	
		<!-- Drug (causality): 
	E2B(R2): element "drug"
	E2B(R3): element "causalityAssessment"
	-->
	<xsl:template match="drug" mode="causality">
		<!-- B.4.k.1 Characterization of Drug Role -->
		<xsl:if test="string-length(drugcharacterization)>0">
			<component typeCode="COMP">
				<causalityAssessment classCode="OBS" moodCode="EVN">
					<code code="{$InterventionCharacterization}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="CE" code="{drugcharacterization}" codeSystem="{$oidDrugRole}" codeSystemVersion="{$oidDrugRoleCSV}"/>
					<!-- Reference to Drug -->
					<subject2 typeCode="SUBJ">
						<productUseReference classCode="SBADM" moodCode="EVN">
							<id root="DID{position()}"/>
						</productUseReference>
					</subject2>
				</causalityAssessment>
			</component>
		</xsl:if>
		<!-- B.4.k.9.r Drug Reaction Matrix -->
		<xsl:variable name="pos" select="position()" />
		<xsl:apply-templates select="drugreactionrelatedness">
			<xsl:with-param name="pos" select="$pos" />
		</xsl:apply-templates>
		
	</xsl:template>
	
	<!-- Drug Reaction Matrix : 
	E2B(R2): element "drugreactionrelatedness"
	E2B(R3): element ""
	-->
	<xsl:template match="drugreactionrelatedness">
	<xsl:param name="pos"/>
	<xsl:choose>
	<!-- See if R2 EU specific drug assessment method is present, if not perform regular free text conversion-->
		<xsl:when test="drugassessmentmethod= 'EVCTM'">
			<component typeCode="COMP">
						<causalityAssessment classCode="OBS" moodCode="EVN">
							<code code="{$Causality}" codeSystem="{$oidObservationCode}" displayName="causality"/>
							<!-- G.k.9.i.2.r.3.EU.1: Result of Assessment - captured in the code field  -->
							<xsl:if test="string-length(drugresult) > 0">
								<value xsi:type="CE" code="{drugresult}" codeSystem="{$oidEUResultofAssessment}" codeSystemVersion="{$oidEUResultofAssessmentCSV}" />
							</xsl:if>
							<!-- G.k.9.i.2.r.2.EU.1: EU Method of assessment - captured in the code field as value 1-->
								<methodCode code="1" codeSystem="{$oidEUMethodofAssessment}" codeSystemVersion="{$oidEUMethodofAssessmentCSV}" />
							<xsl:if test="string-length(drugassessmentsource) > 0">
								<author typeCode="AUT">
									<assignedEntity classCode="ASSIGNED">
										<code code="{drugassessmentsource}" codeSystem="{$oidEUSourceofAssessment}" codeSystemVersion="{$oidEUMethodofAssessmentCSV}" />
										<!-- G.k.9.i.2.r.1.EU.1: EU Source of assessment - captured in the code field-->								
									</assignedEntity>
								</author>
							</xsl:if>
												<!-- Reference to Reaction, if a match is found -->
							<xsl:variable name="reaction" select="drugreactionasses"/>
							<xsl:if test="count(../../reaction[reactionmeddrallt = $reaction or primarysourcereaction = $reaction]) > 0">
								<subject1 typeCode="SUBJ">
									<adverseEffectReference classCode="OBS" moodCode="EVN">
										<xsl:variable name="rid">
											<xsl:for-each select="../../reaction">
												<xsl:if test="reactionmeddrallt = $reaction or primarysourcereaction = $reaction">RID<xsl:value-of select="position()"/></xsl:if>
											</xsl:for-each>
										</xsl:variable>
										<id root="{$rid}"/>
									</adverseEffectReference>
								</subject1>
							</xsl:if>
							<!-- Reference to Drug -->
							<subject2 typeCode="SUBJ">
								<productUseReference classCode="SBADM" moodCode="EVN">
<!--									<xsl:variable name="drug" select="generate-id(..)"/>
									<xsl:variable name="did">
										<xsl:for-each select="../../drug">
											<xsl:if test="generate-id(.) = $drug">DID<xsl:value-of select="position()"/></xsl:if>
										</xsl:for-each>
									</xsl:variable>-->
										<xsl:variable name="did">DID<xsl:value-of select="$pos" /></xsl:variable>
									<id root="{$did}"/>
								</productUseReference>
							</subject2>
						</causalityAssessment>
				</component>
			</xsl:when>	
		<xsl:otherwise>		
			<xsl:if test="string-length(drugassessmentsource) + string-length(drugassessmentmethod) + string-length(drugresult) > 0">
				<component typeCode="COMP">
					<causalityAssessment classCode="OBS" moodCode="EVN">
						<code code="{$Causality}" codeSystem="{$oidObservationCode}"/>
						<!-- B.4.k.9.i.2.r.3 Assessment Result -->
						<xsl:if test="string-length(drugresult) > 0">
							<value xsi:type="ST"><xsl:value-of select="drugresult"/></value>
						</xsl:if>
						<!-- B.4.k.9.i.2.r.2 Assessment Method -->
						<xsl:if test="string-length(drugassessmentmethod) > 0">
							<methodCode>
								<originalText><xsl:value-of select="drugassessmentmethod"/></originalText>
							</methodCode>
						</xsl:if>
						<xsl:if test="string-length(drugassessmentsource) > 0">
							<author typeCode="AUT">
								<assignedEntity classCode="ASSIGNED">
									<code>
										<!-- B.4.k.9.i.2.r.1 Assessment Source -->
										<originalText><xsl:value-of select="drugassessmentsource"/></originalText>
									</code>
								</assignedEntity>
							</author>
						</xsl:if>
						<!-- Reference to Reaction, if a match is found -->
						<xsl:variable name="reaction" select="drugreactionasses"/>
						<xsl:if test="count(../../reaction[reactionmeddrallt = $reaction or primarysourcereaction = $reaction]) > 0">
							<subject1 typeCode="SUBJ">
								<adverseEffectReference classCode="OBS" moodCode="EVN">
									<xsl:variable name="rid">
										<xsl:for-each select="../../reaction">
											<xsl:if test="reactionmeddrallt = $reaction or primarysourcereaction = $reaction">RID<xsl:value-of select="position()"/></xsl:if>
										</xsl:for-each>
									</xsl:variable>
									<id root="{$rid}"/>
								</adverseEffectReference>
							</subject1>
						</xsl:if>
						<!-- Reference to Drug -->
						<subject2 typeCode="SUBJ">
							<productUseReference classCode="SBADM" moodCode="EVN">
							<!--	<xsl:variable name="drug" select="generate-id(..)"/>
								<xsl:variable name="did">
									<xsl:for-each select="../../drug">
										<xsl:if test="generate-id(.) = $drug">DID<xsl:value-of select="position()"/></xsl:if>
									</xsl:for-each>
								</xsl:variable>-->
								<xsl:variable name="did">DID<xsl:value-of select="$pos" /></xsl:variable>
								<id root="{$did}"/>
							</productUseReference>
						</subject2>
					</causalityAssessment>
				</component>
			</xsl:if>
		</xsl:otherwise>
		</xsl:choose>
	</xsl:template>	
</xsl:stylesheet>
