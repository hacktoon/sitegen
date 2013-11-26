<section id="sidebar">
	<h2>Menu</h2>
	<div class="widget">
		<h2>Last pages</h2>
		<ul>
			{%pagelist num="5"%}
				<li>
					<a title="{{each.title}}" href="{{each.permalink}}">
						{{each.date}} - {{each.title}}
					</a>
				</li>
			{%end%}
		</ul>
	</div>
</section>
