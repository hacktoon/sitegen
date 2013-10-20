<section id="sidebar">
	<h2>Menu</h2>
	<div class="widget">
		<h2>Last pages</h2>
		<ul>
			{{list src=pages num=5}}
				<li>
					<a title="{{page.title}}" href="{{page.permalink}}">
						{{page.date}} - {{page.title}}
					</a>
				</li>
			{{end}}
		</ul>
	</div>
	<div class="widget">
		<h2>This page's children</h2>
		<ul>
			{{list num=4 sort=date ord=desc}}
				<li>
					<a title="{{page.title}}" href="{{page.permalink}}">
						{{page.date}} - {{page.title}}
					</a>
				</li>
			{{end}}
		</ul>
	</div>
</section>
